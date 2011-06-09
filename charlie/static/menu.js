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
                var testSetsData = {'action': 'testSets', 'testSetName': testSetsForm.testSetName.getValue()};
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
        }],
    });
    var testSetsStore = new Ext.data.JsonStore({
        url: '/manage/home_data/?action=testSets',
        fields: ['title', 'id'],
        storeId: 'testSetsStore',
        listeners: {'load': function() {
            testCasesGrid.reconfigure(this, testCasesGrid.getColumnModel());
            mainPanel.centerRegion.app.add(testCasesGrid);
            testCasesGrid.show();
            mainPanel.centerRegion.app.add(testSetsForm);
            mainPanel.centerRegion.app.doLayout(true, true);
            mainPanel.centerRegion.doLayout(false);
            mainPanel.centerRegion.app.doLayout(true, true);
            testCasesGrid.setHeight(Math.min(21 * testSetsStore.getCount() + 51, window.innerHeight - 55));
            testCasesGrid.setWidth(300);
        }}
    });
    var tree = new Ext.tree.TreePanel({
        autoWidth: true,
        autoHeight: true,
        root: {
            nodeType: 'async',
            text: 'Administrative Tasks',
            draggable: false,
            id: 'src',
            expanded: true,
        },
        listeners: {
            'click': function(n, e) {
                if(n.isLeaf()) {
                    appTitle = '<h1>' + n.attributes.text + '</h1>';
                    mainPanel.centerRegion.appTitle.update(appTitle);
                    mainPanel.centerRegion.app.removeAll(false);
                    //var currentStore = Ext.StoreMgr.get(n.attributes.value + 'store');
                    var currentStore = Ext.StoreMgr.get('testSetsStore');
                    currentStore.load();
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
