var tsTree;
Ext.onReady(function() {
    Ext.QuickTips.init();
    var form; /*filled by static/newTestcase.jsi
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
                var testSetsData = {'action': 'testSets', 'testSetName': newTestSetForm.testSetName.getValue(), 'parentTestSetId': newTestSetForm.parentTestSetId.getValue()};
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
                id: 'editUser',
                text: 'Edit this User',
            }, {
                id: 'newUser',
                text: 'Create User here',
            }, {
                id: 'delUser',
                text: 'Delete this User',
            }],
            listeners: {'itemclick': function(item) {
                switch(item.id) {
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
                            console.log(result);
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
                id: 'editTeam',
                text: 'Edit this Team',
            }, {
                id: 'newTeam',
                text: 'Create new Team',
            }, {
                id: 'newUserHere',
                text: 'Create a User here',
            }, {
                id: 'delTeam',
                text: 'Delete this Team',
            }],
            listeners: {'itemclick': function(item) {
                switch(item.id) {
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
                id: 'editTestCase',
                text: 'Edit Test Case',
            }, {
                id: 'newTestCase',
                text: 'Create Test Case here',
            }, {
                id: 'delTestCase',
                text: 'Delete this Test Case',
            }],
            listeners: {
                'itemclick': function(item) {
                    switch(item.id) {
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
                }
            },
        }),
        contextMenuNode: new Ext.menu.Menu({
            items: [{
                id: 'editTestSet',
                text: 'Edit Test Set',
            }, {
                id: 'newTestCaseHere',
                text: 'Create Test Case here',
            }, {
                id: 'newTestSet',
                text: 'Create Test Set here',
            }, {
                id: 'delTestSet',
                text: 'Delete this Test Set',
            }],
            listeners: {
                'itemclick': function(item) {
                    var tsid = tsTree.getSelectionModel().getSelectedNode().attributes.tsid;
                    if(tsid == undefined)
                    {
                        tsid = 0;
                    }
                    switch(item.id) {
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
            'dragdrop': function(myTreePanel, selNode, dragdrop, curEvent) {
                var parentTs = selNode.parentNode.attributes.tsid;
                if(parentTs == undefined) {
                    parentTs = -1;
                }
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
                teamsTree.hide();
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
                layout: 'column',
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
