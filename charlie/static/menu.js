var tsTree;
Ext.onReady(function() {
    Ext.QuickTips.init();
    function append_records(myNode, myArray) {
        for(var i = 0; i < myNode.childNodes.length; i++) {
            if(myNode.childNodes[i].isLeaf()) {
                myArray = myArray.concat(new Ext.data.Record({
                    tcid: myNode.childNodes[i].attributes.value,
                    tcname: myNode.childNodes[i].attributes.text,
                }));
            } else {
                myArray = append_records(myNode.childNodes[i], myArray);
            }
        }
        return myArray;
    }
    var form, historyPanel; /*filled by static/newTestcase.jsi
               *contains the fields for test case creation*/
    var comboData = new Ext.data.JsonStore({
        /*contains the fields required to create a new test case*/
        url: '/manage/home_data/?action=combodata',
        fields: ['os', 'module', 'envir', 'browser', 'release', 'version', 'smodule'],
        storeId: 'comboDataStore',
        listeners: {
            'load': function(opts) {
                form = loadForm(comboData);
                form.hide();
                form.add(new Ext.form.Hidden({
                    name: 'tsid',
                    ref: 'tsid',
                }));
                if(opts['leaf']) {
                    var tsid = tsTree.getSelectionModel().getSelectedNode().parentNode.attributes.tsid;
                } else {
                    var tsid = tsTree.getSelectionModel().getSelectedNode().attributes.tsid;
                }
                if(tsid == undefined) {
                    tsid = -1;
                }
                form.tsid.setValue(tsid);
                form.addButton(new Ext.Button({
                    text: 'Save',
                    handler: function() {
                        if (form.form.isValid()) {
                            form.getForm().submit({
                                waitTitle: 'Connecting',
                                url: '/manage/home_data/',
                                waitMsg: 'Sending data...',
                                success: function(f, a) {
                                    Ext.Msg.show({
                                        title: 'Saved',
                                        msg: 'Your test case has been saved',
                                        buttons: Ext.Msg.OK,
                                        icon: Ext.MessageBox.INFO,
                                        fn: function() {
                                            location.reload(true);
                                        }
                                    });
                                },
                                failure: function(f, action) {
                                    Ext.Msg.alert('error ' + action.response.status, action.response.statusText);
                                }
                            });
                        }
                    }
                }));
                /*buttons are not always the same, so here they are...*/
                form.addButton(new Ext.Button({
                    text: 'Reset',
                    handler: function() {
                        form.form.reset();
                    }
                }));
                form.addButton(new Ext.Button({
                    text: 'Cancel',
                    handler: function() {
                        form.hide();
                        tsTree.show();
                    }
                }));
                mainPanel.centerRegion.app.add(form);
                form.show();
                tsTree.hide();
                mainPanel.centerRegion.app.doLayout(true, true);
                form.doLayout();
            },
        },
    });
    var appTitle = '<h1>Choose a task in the left menu</h1>';    /*displays on top of the app*/
    var newUserForm = new Ext.form.FormPanel({
        /*formPanel to create a user*/
        autoHeight: true,
        autoWidth: true,
        padding: 10,
        border: false,
        hidden: true,
        id: 'newUserForm',
        items: [{
            xtype: 'hidden',
            name: 'action',
            value: 'newUser',
        }, {
            xtype: 'textfield',
            name: 'username',
            allowBlank: false,
            fieldLabel: 'User Name',
        }, {
            xtype: 'hidden',
            ref: 'team',
            name: 'team',
        }, {
            xtype: 'checkbox',
            fieldLabel: 'Privileged',
            name: 'privileged',
        }],
        buttons: [{
            xtype: 'button',
            text: 'OK',
            handler: function() {
                if(newUserForm.form.isValid()) {
                    newUserForm.getForm().submit({
                        waitTitle: 'Connecting',
                        url: '/manage/home_data/',
                        waitMsg: 'Sending data...',
                        success: function(form, action) {
                            Ext.Msg.show({
                                title: 'Saved',
                                msg: 'The new user has been saved',
                                buttons: Ext.Msg.OK,
                                icon: Ext.MessageBox.INFO,
                                fn: function() {
                                    location.reload(true);
                                }
                            });
                        },
                        failure: function(form, action) {
                            Ext.Msg.alert('error ' + action.response.status, action.response.statusText);
                        },
                    });
                }
            },
        }, {
            xtype: 'button',
            text: 'Cancel',
            handler: function() {
                newUserForm.hide();
                teamsTree.show();
            },
        }],
    });
    var newTeamForm = new Ext.form.FormPanel({
        /*formPanel to create a new team*/
        autoHeight: true,
        autoWidth: true,
        padding: 10,
        border: false,
        hidden: true,
        id: 'newTeamForm',
        items: [{
            xtype: 'hidden',
            name: 'action',
            value: 'newTeam',
        }, {
            xtype: 'textfield',
            name: 'name',
            allowBlank: false,
            fieldLabel: 'Team Name',
        }],
        buttons: [{
            xtype: 'button',
            text: 'OK',
            handler: function() {
                if(newTeamForm.form.isValid()) {
                    newTeamForm.getForm().submit({
                        waitTitle: 'Connecting',
                        url: '/manage/home_data/',
                        waitMsg: 'Sending data...',
                        success: function(form, action) {
                            Ext.Msg.show({
                                title: 'Saved',
                                msg: 'The new team has been saved',
                                buttons: Ext.Msg.OK,
                                icon: Ext.MessageBox.INFO,
                                fn: function() {
                                    location.reload(true);
                                }
                            });
                        },
                        failure: function(from, action) {
                            Ext.Msg.alert('error ' + action.response.status, action.response.statusText);
                        },
                    });
                }
            },
        }, {
            xtype: 'button',
            text: 'Cancel',
            handler: function() {
                newTeamForm.hide();
                teamsTree.show();
            },
        }],
    });
    var newTestSetForm = new Ext.form.FormPanel({
        /*formPanel for creating a new test set*/
        autoHeight: true,
        width: 300,
        padding: 10,
        border: false,
        buttons: [{
            xtype: 'button',
            autoHeight: true,
            autoWidth: true,
            handler: function(button, curEvent) {
                var selected = testCasesGrid.getSelectionModel().getSelections();
                var testSetsData = {
                    'action': 'testSets',
                    'testSetName': newTestSetForm.testSetName.getValue(),
                    'parentTestSetId': newTestSetForm.parentTestSetId.getValue()
                };
                if(newTestSetForm.form.isValid() && selected.length > 0) {
                    for(i = 0; i < selected.length; i++) {
                        testSetsData['tc' + i] = selected[i].id;
                    }
                    Ext.Ajax.request({
                        method: 'POST',
                        url: '/manage/home_data/',
                        params: testSetsData,
                        success: function(suc) {
                            location.reload(true);
                        },
                        failure: function(suc, err) {
                            Ext.Msg.alert('erreur', err);
                        }
                    });
                }
            },
            text: 'Submit',
        }, {
            xtype: 'button',
            autoHeight: true,
            autoWidth: true,
            text: 'Cancel',
            handler: function(button, curEvent) {
                newTestSetForm.hide();
                testCasesGrid.hide();
                tsTree.show();
            }
        }],
        id: 'newTestSetForm',
        items: [{
            xtype: 'textfield',
            fieldLabel: 'New Test Set Name',
            allowBlank: false,
            ref: 'testSetName',
            name: 'testSetName',
        }, {
            xtype: 'numberfield',
            hidden: true,
            name: 'parentTestSetId',
            ref: 'parentTestSetId',
            value: 0,
        }],
    });
    var testCasesStore = new Ext.data.JsonStore({
        /*store containing all of the test cases*/
        url: '/manage/home_data/?action=testSets',
        fields: ['title', 'id'],
        storeId: 'testCasesStore',
        listeners: {'load': function() {
            testCasesGrid.reconfigure(this, testCasesGrid.getColumnModel());
            mainPanel.centerRegion.app.removeAll(false);
            mainPanel.centerRegion.app.add(testCasesGrid);
            testCasesGrid.show();
            mainPanel.centerRegion.app.add(newTestSetForm);
            newTestSetForm.show();
            mainPanel.centerRegion.doLayout(false);
            mainPanel.centerRegion.app.doLayout(true, true);
            testCasesGrid.setHeight(Math.min(21 * testCasesStore.getCount() + 51, window.innerHeight - 55));
            testCasesGrid.setWidth(300);
        }}
    });
    var teamsTree = new Ext.tree.TreePanel({
        /*treePanel containing the teams and the users*/
        autoHeight: true,
        autoWidth: true,
        enableDD: true,
        root: {
            nodeType: 'async',
            text: 'Teams',
            draggable: false,
            id: 'teamsSrc',
            expanded: true,
        },
        contextMenuLeaf: new Ext.menu.Menu({
            items: [{
                action: 'editUser',
                text: 'Edit this User',
            }, {
                action: 'newUser',
                text: 'Create User here',
            }, {
                action: 'delUser',
                text: 'Delete this User',
            }],
            listeners: {'itemclick': function(item) {
                switch(item.action) {
                case 'newUser':
                    teamsTree.hide();
                    if(teamsTree.getSelectionModel().getSelectedNode().parentNode.attributes.gid == undefined) {
                        newUserForm.team.setValue(-1);
                    } else {
                        newUserForm.team.setValue(teamsTree.getSelectionModel().getSelectedNode().parentNode.attributes.gid);
                    }
                    mainPanel.centerRegion.app.add(newUserForm);
                    newUserForm.show();
                    mainPanel.centerRegion.doLayout(false);
                    mainPanel.centerRegion.app.doLayout(true, true);
                    break;
                case 'editUser':
                    /*edit User*/
                    break;
                case 'delUser':
                    Ext.Ajax.request({
                        method: 'GET',
                        url: '/manage/home_data/?action=deluser&u=' + teamsTree.getSelectionModel().getSelectedNode().attributes.uid,
                        success: function(response, options) {
                            var result = Ext.util.JSON.decode(response.responseText);
                            if(result.success) {
                                location.reload(true);
                            } else {
                                Ext.Msg.alert("error", result.errorMessage);
                            }
                        },
                        failure: function(response, options) {
                            var result = Ext.util.JSON.decode(response.responseText);
                            Ext.Msg.alert("error", result.errorMessage);
                        },
                    });
                    break;
                }
            }},
        }),
        contextMenuNode: new Ext.menu.Menu({
            items: [{
                action: 'editTeam',
                text: 'Edit this Team',
            }, {
                action: 'newTeam',
                text: 'Create new Team',
            }, {
                action: 'newUserHere',
                text: 'Create a User here',
            }, {
                action: 'delTeam',
                text: 'Delete this Team',
            }],
            listeners: {'itemclick': function(item) {
                switch(item.action) {
                case 'newUserHere':
                    teamsTree.hide();
                    if(teamsTree.getSelectionModel().getSelectedNode().attributes.gid == undefined) {
                        newUserForm.team.setValue(-1);
                    } else {
                        newUserForm.team.setValue(teamsTree.getSelectionModel().getSelectedNode().attributes.gid);
                    }
                    mainPanel.centerRegion.app.add(newUserForm);
                    newUserForm.show();
                    mainPanel.centerRegion.doLayout(false);
                    mainPanel.centerRegion.app.doLayout(true, true);
                    break;
                case 'newTeam':
                    teamsTree.hide();
                    mainPanel.centerRegion.app.add(newTeamForm);
                    newTeamForm.show();
                    mainPanel.centerRegion.doLayout(false);
                    mainPanel.centerRegion.app.doLayout(true, true);
                    break;
                case 'editTeam':
                    /*edit team*/
                    break;
                case 'delTeam':
                    if(teamsTree.getSelectionModel().getSelectedNode() != teamsTree.getRootNode()) {
                        Ext.Ajax.request({
                            method: 'GET',
                            url: '/manage/home_data/?action=delteam&t=' + teamsTree.getSelectionModel().getSelectedNode().attributes.gid,
                            success: function(response, options) {
                                location.reload(true);
                            },
                            failure: function(response, options) {
                                Ext.Msg.alert("error", "the team couldn't be deleted");
                            },
                        });
                    }
                    break;
                }
            }},
        }),
        listeners: {
            'dragdrop': function(myTreePanel, selNode, dragdrop, curEvent) {
                var team = selNode.parentNode.attributes.gid;
                if(team == undefined) {
                    team = -1;
                }
                if(selNode.isLeaf()) {
                    Ext.Ajax.request({
                        method: 'GET',
                        url: '/manage/home_data/?action=mvuser&team=' + team + '&user=' + selNode.attributes.uid,
                    });
                    teamsTree.getLoader().load(new Ext.tree.AsyncTreeNode({
                        nodeType: 'async',
                        text: 'Teams',
                        draggable: false,
                        id: 'teamsSrc',
                        expanded: true,
                    }));
                }
            },
            'contextmenu': function(selNode, curEvent) {
                selNode.select();
                var myCtxtMenu;
                if(selNode.isLeaf()) {
                    myCtxtMenu = selNode.getOwnerTree().contextMenuLeaf;
                } else {
                    myCtxtMenu = selNode.getOwnerTree().contextMenuNode;
                }
                myCtxtMenu.contextNode = selNode;
                myCtxtMenu.showAt(curEvent.getXY());
            }
        },
    });
    tsTree = new Ext.tree.TreePanel({
        /*treePanel containing test cases and test sets*/
        autoHeight: true,
        autoWidth: true,
        enableDD: true,
        root: {
            nodeType: 'async',
            text: 'Test Sets',
            draggable: false,
            id: 'tsSrc',
            expanded: true,
        },
        contextMenuLeaf: new Ext.menu.Menu({
            items: [{
                action: 'editTestCase',
                text: 'Edit Test Case',
            }, {
                action: 'newTestCase',
                text: 'Create Test Case here',
            }, {
                action: 'delTestCase',
                text: 'Delete this Test Case',
            }],
            listeners: {
                'itemclick': function(item) {
                    switch(item.action) {
                    case 'editTestCase':
                        /*edit test case*/
                        break;
                    case 'newTestCase':
                        tsTree.hide();
                        comboData.load({'leaf': true});
                        break;
                    case 'delTestCase':
                        Ext.Ajax.request({
                            method: 'GET',
                            url: '/manage/home_data/?action=deltc&tc=' + tsTree.getSelectionModel().getSelectedNode().attributes.value,
                            success: function(response, options) {
                                location.reload(true);
                            },
                            failure: function(response, options) {
                                Ext.Msg.alert("error", "the team couldn't be deleted");
                            },
                        });
                        break;
                    }
                },
            },
        }),
        contextMenuNode: new Ext.menu.Menu({
            items: [{
                action: 'editTestSet',
                text: 'Edit Test Set',
            }, {
                action: 'newTestCaseHere',
                text: 'Create Test Case here',
            }, {
                action: 'newTestSet',
                text: 'Create Test Set here',
            }, {
                action: 'delTestSet',
                text: 'Delete this Test Set',
            }],
            listeners: {
                'itemclick': function(item) {
                    var tsid = tsTree.getSelectionModel().getSelectedNode().attributes.tsid;
                    if(tsid == undefined)
                    {
                        tsid = 0;
                    }
                    switch(item.action) {
                    case 'newTestCaseHere':
                        tsTree.hide();
                        comboData.load({'leaf': false});
                        break;
                    case 'editTestSet':
                        /*edit test set*/
                        break;
                    case 'newTestSet':
                        tsTree.hide();
                        newTestSetForm.parentTestSetId.setValue(tsid);
                        testCasesStore.load();
                        break;
                    case 'delTestSet':
                        if(tsTree.getSelectionModel().getSelectedNode() != tsTree.getRootNode()) {
                            Ext.Ajax.request({
                                method: 'GET',
                                url: '/manage/home_data/?action=delts&ts=' + tsid,
                                success: function(response, options) {
                                    location.reload(true);
                                },
                                failure: function(response, options) {
                                    Ext.Msg.alert("error", "the team couldn't be deleted");
                                },
                            });
                        }
                        break;
                    }
                }
            },
        }),
        listeners: {
            'dragdrop': function(myTree, selNode, dragdrop, curEvent) {
                var myMenu = new Ext.menu.Menu({
                    items: [{
                        action: 'moveIt',
                        text: 'Move here',
                    }, {
                        action: 'copyIt',
                        text: 'Copy here',
                    }],
                    listeners: {
                        'itemclick': function(item) {
                            switch(item.action) {
                            case 'moveIt':
                                myTree.dropAction = 'move';
                                if(selNode.isLeaf()) {
                                    Ext.Ajax.request({
                                        method: 'GET',
                                        url: '/manage/home_data/?action=mvtc&ts=' + parentTs + '&tc=' + selNode.attributes.value,
                                    });
                                } else {
                                    Ext.Ajax.request({
                                        method: 'GET',
                                        url: '/manage/home_data/?action=mvts&pts=' + parentTs + '&cts=' + selNode.attributes.tsid,
                                    });
                                }
                                break;
                            case 'copyIt':
                                myTree.dropAction = 'copy';
                                if(selNode.isLeaf()) {
                                    Ext.Ajax.request({
                                        method: 'GET',
                                        url: '/manage/home_data/?action=cptc&ts=' + parentTs + '&tc=' + selNode.attributes.value,
                                    });
                                } else {
                                    Ext.Ajax.request({
                                        method: 'GET',
                                        url: '/manage/home_data/?action=cpts&pts=' + parentTs + '&cts=' + selNode.attributes.tsid,
                                    });
                                }
                                location.reload(true);
                                break;
                            }
                        },
                    },
                }).showAt(curEvent.getXY());
                var parentTs = selNode.parentNode.attributes.tsid;
                if(parentTs == undefined) {
                    parentTs = -1;
                }
            },
            'contextmenu': function(selNode, curEvent) {
                selNode.select();
                var myCtxtMenu;
                if(selNode.isLeaf()) {
                    myCtxtMenu = selNode.getOwnerTree().contextMenuLeaf;
                } else {
                    myCtxtMenu = selNode.getOwnerTree().contextMenuNode;
                }
                myCtxtMenu.contextNode = selNode;
                myCtxtMenu.showAt(curEvent.getXY());
            },
        },
    });
    var tree = new Ext.tree.TreePanel({
        /*treePanel containing the main management menu*/
        autoWidth: true,
        autoHeight: true,
        root: {
            nodeType: 'async',
            text: 'Administrative Tasks',
            draggable: false,
            id: 'menuSrc',
            expanded: true,
        },
        listeners: {
            'click': function(n, e) {
                if(form != undefined) { form.hide(); }
                if(historyPanel != undefined) { historyPanel.hide() };
                teamsTree.hide();
                newSessPanel.hide();
                newUserForm.hide();
                newTeamForm.hide();
                newTestSetForm.hide();
                tsTree.hide();
                testCasesGrid.hide();
                if(n.isLeaf()) {
                    appTitle = '<h1>' + n.attributes.text + '</h1>';
                    mainPanel.centerRegion.appTitle.update(appTitle);
                    if(n.attributes.value == "testSets") {
                        tsTree.getLoader().dataUrl = '/manage/home_ts/';
                        tsTree.getLoader().load(new Ext.tree.AsyncTreeNode({
                            nodeType: 'async',
                            text: 'Test Sets',
                            draggable: false,
                            id: 'tsSrc',
                            expanded: true,
                        }));
                        tsTree.doLayout(true);
                        tsTree.show();
                        mainPanel.centerRegion.app.add(tsTree);
                        mainPanel.centerRegion.doLayout(false);
                        mainPanel.centerRegion.app.doLayout(true, true);
                    } else if(n.attributes.value == 'history') {
                        historyPanel = new Ext.Panel({
                            autoDestroy: true,
                            ref: 'history',
                            id: 'history',
                            hidden: true,
                            baseCls: 'x-plain',
                            autoWidth: true,
                            autoHeight: true,
                            layout: 'table',
                            layoutConfig: {
                                columns: 3,
                            },
                            defaults: {
                                margin: 3,
                                flex: 3,
                                padding: 3,
                                width: 250,
                                autoHeight: true,
                            },
                            listeners: {
                                'show': function(myPanel) {
                                    var sessions = new Ext.data.JsonStore({
                                        autoDestroy: true,
                                        method: 'GET',
                                        url: '/manage/home_data/?action=history',
                                        fields: [{
                                            name: 'name',
                                            type: 'string',
                                        }, {
                                            name: 'from',
                                            type: 'date',
                                        }, {
                                            name: 'to',
                                            type: 'date',
                                        }, {
                                            name: 'group',
                                            type: 'int',
                                        }],
                                        listeners: {
                                            'load': function(myStore, myRecs) {
                                                for(var i = 0; i < myRecs.length; i++) {
                                                    myPanel.add({
                                                        xtype: 'panel',
                                                        autoDestroy: true,
                                                        title: myRecs[i].json.name,
                                                        html: "<a class='hist' href='/manage/current/?s=" + myRecs[i].json.id + "'><p>" + myRecs[i].json.from + " to " + myRecs[i].json.to + "</p><p>assigned to " + myRecs[i].json.teamname + "</p></a>",
                                                        bbar: {
                                                            layout: {
                                                                type: 'hbox',
                                                                align: 'top',
                                                            },
                                                            items: [{
                                                                xtype: 'checkbox',
                                                                autoShow: true,
                                                                autoDestroy: true,
                                                                checked: myRecs[i].json.disp,
                                                                tsr: myRecs[i].json.id,
                                                                boxLabel: 'Keep on the "Current sessions" calendar',
                                                                listeners: {
                                                                    'check': function(myCBox, checked) {
                                                                        Ext.Ajax.request({
                                                                            method: 'POST',
                                                                            url: '/manage/home_data/',
                                                                            params: {
                                                                                'tsr': myCBox.tsr,
                                                                                'disp': checked,
                                                                                'action': 'chgdisp',
                                                                            },
                                                                        });
                                                                    },
                                                                },
                                                            }],
                                                        },
                                                    });
                                                }
                                                myPanel.doLayout(true, true);
                                                mainPanel.centerRegion.app.doLayout(true, true);
                                            },
                                        },
                                    });
                                    sessions.load();
                                },
                            },
                        });
                        mainPanel.centerRegion.app.add(historyPanel);
                        historyPanel.show();
                    } else if(n.attributes.value == 'newSession') {
                        mainPanel.centerRegion.app.add(newSessPanel);
                        newSessPanel.doLayout(true, true);
                        newSessPanel.show();
                        newSessPanel.doLayout(true, true);
                        mainPanel.centerRegion.app.doLayout(true, true);
                    } else if(n.attributes.value == 'currentSession') {
                        window.location = "/manage/current/";
                    } else if(n.attributes.value == 'teams') {
                        teamsTree.getLoader().dataUrl = '/manage/home_teams/';
                        teamsTree.getLoader().load(new Ext.tree.AsyncTreeNode({
                            nodeType: 'async',
                            text: 'Teams',
                            draggable: false,
                            id: 'teamsSrc',
                            expanded: true,
                        }));
                        teamsTree.show();
                        mainPanel.centerRegion.app.add(teamsTree);
                        mainPanel.centerRegion.doLayout(false);
                        mainPanel.centerRegion.app.doLayout(true, true);
                    }
                }
            },
        },
        dataUrl: '/manage/home_menu/',
    });
    var newSessPanel = new Ext.Panel({
        ref: 'newsess',
        id: 'newsess',
        hidden: true,
        layout: 'table',
        padding: 8,
        layoutConfig: {
            columns: 2,
        },
        defaults: {
            width: 300,
            padding: 8,
        },
        items: [{
            xtype: 'form',
            colspan: 2,
            ref: 'nsform',
            border: true,
            width: 600,
            height: 200,
            padding: 8,
            id: 'newsessname',
            isOK: function() {
                var form_ok = false, dates_ok = false, grid_ok = false;
                if(newSessPanel.nsform.getForm().isValid())
                    form_ok = true;
                if(newSessPanel.nsform.startdate.getValue() < newSessPanel.nsform.enddate.getValue())
                    dates_ok = true;
                if(newSessPanel.sgrid.getStore().getCount() > 0)
                    grid_ok = true;
                if(form_ok && dates_ok && grid_ok) {
                    return {'success': true};
                } else {
                    var errormsg = "";
                    if(!form_ok) {
                        errormsg += "Fill in the form Properly. ";
                    }
                    if(!dates_ok) {
                        errormsg += "Start date must be the earliest. ";
                    }
                    if(!grid_ok) {
                        errormsg += "Select at least one test case. ";
                    }
                    return {'success': false, 'error': errormsg};
                }
            },
            items: [{
                xtype: 'textfield',
                ref: 'sessname',
                allowBlank: false,
                fieldLabel: 'New session Name',
                width: 250,
            }, {
                xtype: 'datefield',
                ref: 'startdate',
                allowBlank: false,
                fieldLabel: 'Starting Date',
                width: 250,
            }, {
                xtype: 'datefield',
                ref: 'enddate',
                allowBlank: false,
                fieldLabel: 'Ending Date',
                width: 250,
            }, {
                xtype: 'combo',
                ref: 'group',
                allowBlank: false,
                fieldLabel: 'Assign to team',
                width: 250,
                editable: false,
                mode: 'remote',
                store: new Ext.data.JsonStore({
                    fields: [{
                        name: 'gname', type: 'string',
                    }, {
                        name: 'gid', type: 'int',
                    }],
                    proxy: new Ext.data.HttpProxy({
                        method: 'GET',
                        url: '/manage/home_data/?action=getgroups',
                    }),
                }),
                forceSelection: true,
                triggerAction: 'all',
                displayField: 'gname',
                valueField: 'gid',
            }],
            buttons: [{
                text: 'Save',
                handler: function(myButton, myEvent) {
                    var test_form = newSessPanel.nsform.isOK();
                    if(test_form.success) {
                        var ajaxParams = {
                                'action': 'newtestsetrun',
                                'name': newSessPanel.nsform.sessname.getValue(),
                                'from_y': newSessPanel.nsform.startdate.getValue().format('Y'),
                                'to_y': newSessPanel.nsform.enddate.getValue().format('Y'),
                                'from_m': newSessPanel.nsform.startdate.getValue().format('m'),
                                'to_m': newSessPanel.nsform.enddate.getValue().format('m'),
                                'from_d': newSessPanel.nsform.startdate.getValue().format('d'),
                                'to_d': newSessPanel.nsform.enddate.getValue().format('d'),
                                'group': newSessPanel.nsform.group.getValue(),
                        };
                        for(var i = 0; i < newSessPanel.sgrid.getStore().getCount(); i++) {
                            ajaxParams['tcid' + i] = newSessPanel.sgrid.getStore().getAt(i).data.tcid;
                            ajaxParams['tcname' + i] = newSessPanel.sgrid.getStore().getAt(i).data.tcname;
                        }
                        Ext.Ajax.request({
                            method: 'POST',
                            url: '/manage/home_data/',
                            params: ajaxParams,
                            success: function(response, opts) {
                                Ext.Msg.show({
                                    title: 'Saved',
                                    msg: 'The session has been created',
                                    buttons: Ext.Msg.OK,
                                    icon: Ext.MessageBox.INFO,
                                    fn: function() {
                                        location.reload(true);
                                    },
                                });
                            },
                            failure: function(response, opts) {
                                Ext.Msg.show({
                                    title: 'An error occured',
                                    msg: 'Unable to create the session',
                                    buttons: Ext.Msg.OK,
                                    icon: Ext.MessageBox.WARNING,
                                });
                            },
                        });
                    } else {
                        Ext.Msg.alert("Error", test_form.error);
                    }
                },
            }, {
                text: 'Cancel',
                handler: function(myButton, myEvent) {
                    newSessPanel.hide();
                },
            }],
        }, {
            xtype: 'treepanel',
            height: 400,
            autoScroll: true,
            border: true,
            ref: 'stree',
            root: {
                nodeType: 'async',
                text: 'Test Sets',
                draggable: false,
                id: 'tsSrcNode',
                expanded: true,
            },
            dataUrl: '/manage/home_ts/',
            listeners: {
                'click': function(myNode, myEvent) {
                    if(myNode.isLeaf()) {
                        newSessPanel.sgrid.getStore().add([new Ext.data.Record({
                            tcid: myNode.attributes.value,
                            tcname: myNode.attributes.text,
                        })]);
                    } else {
                        newSessPanel.sgrid.getStore().add(append_records(myNode, []));
                    }
                },
            },
        }, new Ext.grid.GridPanel({
            autoWidth: true,
            enableColumnHide: false,
            enableColumnMove: false,
            enableColumnResize: false,
            enableHdMenu: false,
            height: 400,
            border: true,
            autoScroll: true,
            ref: 'sgrid',
            bbar: [{
                text: 'Reset',
                handler: function(myButton) {
                    newSessPanel.sgrid.getStore().removeAll();
                },
            }, {
                text: 'Remove...',
                enableToggle: true,
                id: 'rm_button',
                handler: function(myButton) {
                    var selected = newSessPanel.sgrid.getSelectionModel().getSelections();
                    if(selected.length > 0) {
                        myButton.toggle();
                        for(var i = 0; i < selected.length; i++) {
                            newSessPanel.sgrid.getStore().remove(selected[i]);
                        }
                    }
                },
            }],
            columns: [{
                id: 'tcid', header: 'Test Case Name', dataIndex: 'tcname', sortable: true, width: 280,
            }],
            store: new Ext.data.ArrayStore({
                fields: [{
                    name: 'tcid', type: 'string',
                }, {
                    name: 'tcname', type: 'string',
                }],
            }),
            listeners: {
                'cellclick': function(myGrid, myRow, myColumn, myEvent) {
                    var rm_button = Ext.getCmp('rm_button');
                    if(rm_button.pressed) {
                        myGrid.getStore().removeAt(myRow);
                    }
                },
                'celldblclick': function(myGrid, myRow, myColumn, myEvent) {
                    myGrid.getStore().removeAt(myRow);
                },
            },
        })],
    });
    var testCasesGrid = new Ext.grid.GridPanel({
        /*grid containing all of the test cases*/
        title: 'Choose the test cases',
        columns: [{
    id: 'id', header: 'Test Cases', dataIndex: 'title', autoWidth: true,
        }],
        id: 'appContent',
        store: testCasesStore,
        stripeRows: true,
        autoExpandColumn: 'id',
        disableSelection: false,
        enableColumnHide: false,
        enableColumnMove: false,
        enableColumnResize: false,
        enableHdMenu: false,
        hidden: true,
    });
    var mainPanel = new Ext.Viewport({
        /*main container of the app*/
        layout: 'border',
        hideBorders: true,
        items: [{
            region: 'north',
            html: '<h1 id="main_title">Charlie Management | <a href="/logout/">Logout</a></h1>',
            autoHeight: true,
            hideBorders: true,
            margins: '0 0 0 0',
        },{
            region: 'center',
            xtype: 'panel',
            ref: 'centerRegion',
            id: 'centerRegion',
            layout: 'border',
            items: [{
                xtype: 'panel',
                hideBorders: true,
                region: 'north',
                ref: 'appTitle',
                html: appTitle,
            },{
                xtype: 'panel',
                hideBorders: true,
                region: 'center',
                ref: 'app',
                id: 'app',
            }],
        },{
            region: 'west',
            width: 300,
            xtype: 'panel',
            margins: '0 0 0 0',
            items: [tree],
        }],
    });
});
