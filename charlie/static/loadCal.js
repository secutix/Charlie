function loadCalendar(tester_visa, tester_id, st) {
    /* provided a tester and test case runs (in the "st" var), returns a CalendarPanel */
    var cal;
    var events = [];
    var nbEvents = st.getTotalCount();
    /* storage of the events in a js array */
    for(i = 0; i < nbEvents; i++) {
        fieldData = st.getAt(i);
        var startDate = new Date(fieldData.json.execution_date).clearTime();
        var endDate = new Date(fieldData.json.execution_date).clearTime().add(Date.DAY, 1).add(Date.SECOND, -1);
        var cal_id = 1;
        switch(fieldData.json.status) {
        case 1:
            cal_id = 2;
            break
        case 2:
            cal_id = 3;
            break
        case 3:
            cal_id = 4;
            break
        case 4:
            cal_id = 5;
            break
        }
        var new_event = {
            'id': fieldData.json.tcrid,
            'cid': cal_id,
            'title': fieldData.json.title,
            'start': startDate,
            'end': endDate,
            'ad': true,
        }
        if(fieldData.json.user != undefined) {
            new_event['uid'] = fieldData.json.user;
        }
        if(fieldData.json.pct != undefined) {
            new_event['pct'] = fieldData.json.pct;
        }
        events = events.concat(new_event);
    }
    var eventData = {
        'evts': events,
    };
    Ext.ns('Ext.charlie');
    Ext.charlie.CalendarData = {
        'calendars': [{
            'id': 1,
            'title': 'Not started',
            'color': 33    /*grey*/
        },{
            'id': 2,
            'title': 'Started',
            'color': 25   /*pale green*/
        },{
            'id': 3,
            'title': 'Error',
            'color': 6   /*orange*/
        },{
            'id': 4,
            'title': 'Completed with errors',
            'color': 2   /*red*/
        },{
            'id': 5,
            'title': 'Completed without errors',
            'color': 27   /*green*/
        }]
    };
    Ext.charlie.CalendarStore = Ext.extend(Ext.data.Store, {
        constructor: function(config){
            config = Ext.applyIf(config || {}, {
                storeId: 'calendarStore',
                root: 'calendars',
                idProperty: Ext.ensible.cal.CalendarMappings.CalendarId.mapping || 'id',
                proxy: new Ext.data.MemoryProxy(),
                fields: Ext.ensible.cal.CalendarRecord.prototype.fields.getRange(),
                sortInfo: {
                    field: Ext.ensible.cal.CalendarMappings.Title.name,
                    direction: 'ASC'
                }
            });
            this.reader = new Ext.data.JsonReader(config);
            Ext.charlie.CalendarStore.superclass.constructor.call(this, config);
        }
    });
    Ext.charlie.MemoryEventStore = Ext.extend(Ext.data.Store, {
        constructor: function(config){
            config = Ext.applyIf(config || {}, {
                storeId: 'eventStore',
                root: 'evts',
                proxy: new Ext.data.MemoryProxy(),
                writer: new Ext.data.DataWriter(),
                fields: Ext.ensible.cal.EventRecord.prototype.fields.getRange(),
                idProperty: Ext.ensible.cal.EventMappings.EventId.mapping || 'id'
            });
            this.reader = new Ext.data.JsonReader(config);
            Ext.charlie.MemoryEventStore.superclass.constructor.call(this, config);
            if(config.autoMsg !== false){
                this.on('write', this.onWrite, this);
            }

            this.initRecs();
        },
        initRecs: function(){
            this.each(function(rec){
                rec.store = this;
                rec.phantom = false;
            }, this);
        },

        onWrite: function(store, action, data, resp, rec){
            if(Ext.charlie.msg){
                if(Ext.isArray(rec)){
                    Ext.each(rec, function(r){
                        this.onWrite.call(this, store, action, data, resp, r);
                    }, this);
                }
            }
        },

        onCreateRecords : function(success, rs, data) {
            if(Ext.isArray(rs)){
                Ext.each(rs, function(rec){
                    this.onCreateRecords.call(this, success, rec, data);
                }, this);
            }
            else {
                rs.phantom = false;
                rs.data[Ext.ensible.cal.EventMappings.EventId.name] = rs.id;
                rs.commit();
            }
        }
    });
    /* actual calendarPanel */
    cal = new Ext.ensible.cal.CalendarPanel({
        id: tester_visa + "_cal",
        activeItem: 2,
        enableEditDetails: false,
        calendarStore: new Ext.charlie.CalendarStore({data: Ext.charlie.CalendarData}),
        eventStore: new Ext.charlie.MemoryEventStore({data: eventData}),
        eventList: eventData,
        title: tester_visa + "'s planning",
        showDayView: false,
        showWeekView: false,
        showMonthView: false,
        multiWeekViewCfg: {
            enableContextMenus: false,
            ddGroup: 'calendarDD',
            user: tester_visa,
            uid: tester_id,
            listeners: {
                'rangeselect': function(cal, dates) {
                    return false;
                },
            },
        },
        autoWidth: true,
        height: 350,
        listeners: {
            'eventupdate': testCaseMoved,
            'eventmove': testCaseMoved,
            'dayClick': function() {
                return false;
            },
        },
    });
    return cal;
}
