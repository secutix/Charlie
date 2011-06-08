Ext.onReady(function() {
    Ext.QuickTips.init();
    var appTitle = new Ext.Panel({
        ref: 'appTitle',
        html: '<h1>Choose a task in the left menu</h1>',
    });
    var testSetsStore = new Ext.data.JsonStore({
        url: '/manage/home_data/?action=testsets',
        fields: ['title', 'id'],
        storeId: 'testSetsStore',
        listeners: {'load': function() {
            testCasesGrid.reconfigure(this, testCasesGrid.getColumnModel());
            mainPanel.centerRegion.add(testCasesGrid);
            testCasesGrid.show();
            mainPanel.centerRegion.doLayout();
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
                    appTitle.update('<h1>' + n.attributes.text + '</h1>');
                    mainPanel.centerRegion.remove('appContent', false);
                    mainPanel.centerRegion.add(appTitle);
                    //var currentStore = Ext.StoreMgr.get(n.attributes.value + 'store');
                    var currentStore = Ext.StoreMgr.get('testSetsStore');
                    currentStore.load();
                }
            },
        },
        dataUrl: '/manage/home_menu/',
    });
    var testCasesGrid = new Ext.grid.GridPanel({
        title: '1. select test cases',
        columns: [{id: 'id', header: 'Test Cases', dataIndex: 'title', width: 300}],
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
            layourt: 'fit',
            ref: 'centerRegion',
            id: 'centerRegion',
            items: [appTitle],
        },{
            region: 'west',
            width: 400,
            xtype: 'panel',
            margins: '0 0 0 0',
            items: [tree],
        }],
    });
});
