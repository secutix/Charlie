Ext.onReady(function() {
    Ext.QuickTips.init();
    var appTitle = '<h1>Choose a task in the left menu</h1>';
    var testSetsForm = new Ext.form.FormPanel({
        autoHeight: true,
        width: 300,
        padding: 10,
        border: false,
        buttons: [{
            xtype: 'button',
            autoHeight: true,
            autoWidth: true,
            handler: function(b, e) {
                var selected = testCasesGrid.getSelectionModel().getSelections();
                var testSetsData = {'action': 'testSets', 'testSetName': testSetsForm.testSetName.getValue(), 'parentTestSetId': testSetsForm.parentTestSetId.getValue()};
                if(testSetsForm.form.isValid() && selected.length > 0) {
                    for(i = 0; i < selected.length; i++) {
                        testSetsData['tc' + i] = selected[i].id;
                    }
                    Ext.Ajax.request({
                        method: 'POST',
                        url: '/manage/home_data/',
                        params: testSetsData,
                        success: function(suc) {
                            Ext.Msg.alert('ok', 'ok');
                        },
                        failure: function(suc, err) {
                            Ext.Msg.alert('erreur', err);
                        }
                    });
                }
            },
            text: 'Submit',
        }],
        id: 'testSetsForm',
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
    var testSetsStore = new Ext.data.JsonStore({
        url: '/manage/home_data/?action=testSets',
        fields: ['title', 'id'],
        storeId: 'testSetsStore',
        listeners: {'load': function() {
            testCasesGrid.reconfigure(this, testCasesGrid.getColumnModel());
            mainPanel.centerRegion.app.removeAll(false);
            mainPanel.centerRegion.app.add(testCasesGrid);
            testCasesGrid.show();
            mainPanel.centerRegion.app.add(testSetsForm);
            mainPanel.centerRegion.doLayout(false);
            mainPanel.centerRegion.app.doLayout(true, true);
            testCasesGrid.setHeight(Math.min(21 * testSetsStore.getCount() + 51, window.innerHeight - 55));
            testCasesGrid.setWidth(300);
        }}
    });
    var tsTree = new Ext.tree.TreePanel({
        autoHeight: true,
        width: 300,
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
                text: 'Edit Test Set',
            }, {
                id: 'newTestCase1',
                text: 'Create Test Case here',
            }, {
                id: 'delTestCase',
                text: 'Delete this Test Case',
            }],
            listeners: {
                'itemclick': function(item) {
                    switch(item.id) {
                    case 'editTestCase':
                        /*edit test set*/
                        break;
                    case 'newTestCase1':
                        /*create test case*/
                        break;
                    case 'delTestCase':
                        /*delete test set*/
                        break;
                    }
                    mainPanel.centerRegion.app.removeAll(false);
                }
            },
        }),
        contextMenuNode: new Ext.menu.Menu({
            items: [{
                id: 'editTestSet',
                text: 'Edit Test Set',
            }, {
                id: 'newTestSet',
                text: 'Create Test Set here',
            }, {
                id: 'newTestCase2',
                text: 'Create Test Case here',
            }, {
                id: 'delTestSet',
                text: 'Delete this Test Set',
            }],
            listeners: {
                'itemclick': function(item) {
                    var tsid = tsTree.getSelectionModel().getSelectedNode().attributes.tsid;
                    switch(item.id) {
                    case 'editTestSet':
                        /*edit test set*/
                        break;
                    case 'newTestCase2':
                        /*create test case*/
                        break;
                    case 'newTestSet':
                        testSetsForm.parentTestSetId.setValue(tsid);
                        testSetsStore.load();
                        break;
                    case 'delTestSet':
                        Ext.Ajax.request({
                            method: 'GET',
                            url: '/manage/home_data/?action=delts&ts=' + tsid,
                            success: function(a) {
                                tree.fireEvent('click', tree.getNodeById('testSetsMenu'));
                            }
                        });
                        break;
                    }
                }
            },
        }),
        listeners: {
            'contextmenu': function(n, e) {
                n.select();
                var c;
                if(n.isLeaf()) {
                    c = n.getOwnerTree().contextMenuLeaf;
                } else {
                    c = n.getOwnerTree().contextMenuNode;
                }
                c.contextNode = n;
                c.showAt(e.getXY());
            }
        },
    });
    var tree = new Ext.tree.TreePanel({
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
                mainPanel.centerRegion.app.removeAll(false);
                if(n.isLeaf()) {
                    appTitle = '<h1>' + n.attributes.text + '</h1>';
                    mainPanel.centerRegion.appTitle.update(appTitle);
                    //var currentStore = Ext.StoreMgr.get(n.attributes.value + 'store');
                    /*var currentStore = Ext.StoreMgr.get('testSetsStore');
                    currentStore.load();*/
                    if(n.attributes.value == "testSets") {
                        tsTree.getLoader().dataUrl = '/manage/home_ts/';
                        tsTree.getLoader().load(new Ext.tree.AsyncTreeNode({
                            nodeType: 'async',
                            text: 'Test Sets',
                            draggable: false,
                            id: 'tsSrc',
                            expanded: true,
                        }));
                        mainPanel.centerRegion.app.add(tsTree);
                        mainPanel.centerRegion.doLayout(false);
                        mainPanel.centerRegion.app.doLayout(true, true);
                    }
                }
            },
        },
        dataUrl: '/manage/home_menu/',
    });
    var testCasesGrid = new Ext.grid.GridPanel({
        title: 'Choose the test cases',
        columns: [{
            id: 'id', header: 'Test Cases',
            dataIndex: 'title', width: 300,
        }],
        id: 'appContent',
        store: testSetsStore,
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
        layout: 'border',
        items: [{
            region: 'north',
            html: '<h1 id="main_title">Charlie Management | <a href="/logout/">Logout</a></h1>',
            autoHeight: true,
            margins: '0 0 0 0',
        },{
            region: 'center',
            xtype: 'panel',
            ref: 'centerRegion',
            id: 'centerRegion',
            layout: 'border',
            items: [{
                xtype: 'panel',
                region: 'north',
                ref: 'appTitle',
                html: appTitle,
            },{
                xtype: 'panel',
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
