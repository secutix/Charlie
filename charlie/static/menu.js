Ext.onReady(function() {
    Ext.QuickTips.init();
    var tcscJsStore = new Ext.data.JsonStore({
        url: '/manage/home_tcsc/',
        fields: ['title', 'id'],
        storeId: 'tcscJsStore',
        listeners: {'load': function() {
            tcscGrid.reconfigure(this, tcscGrid.getColumnModel());
            tcscGrid.show();
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
            expanded: true
        },
        listeners: {
            'click': function(n, e) {
                if(n.isLeaf()) {
                    tcscJsStore.load();
                }
            }
        },
        dataUrl: '/manage/home_menu/'
    });
    var tcscGrid = new Ext.grid.GridPanel({
        title: '1. select test cases',
        columns: [{id: 'id', header: 'Test Cases', dataIndex: 'title', width: 300}],
        store: tcscJsStore,
        stripeRows: true,
        autoExpandColumn: 'id',
        stateful: true,
        stateId: 'tcscGrid',
        disableSelection: false,
        enableColumnHide: false,
        enableColumnMove: false,
        enableColumnResize: false,
        enableHdMenu: false,
        autoHeight: true,
        hidden: true,
        width: 300,
    });
    var mainPanel = new Ext.Viewport({
        layout: 'border',
        items: [{
            region: 'north',
            html: '<h1 id="maintitle">Charlie Management | <a href="/logout/">Logout</a></h1>',
            autoHeight: true,
            margins: '0 0 0 0'
        },{
            region: 'center',
            xtype: 'panel',
            ref: 'main',
            id: 'testcasesView',
            items: [tcscGrid]
        },{
            region: 'west',
            width: 400,
            xtype: 'panel',
            margins: '0 0 0 0',
            items: [tree]
        }]
    });
});
