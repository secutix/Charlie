function loadCalendar(tester_visa, tester_id, st/*, usersStore*/) {
    var cal;
    var events = [];
    var nbEvents = st.getTotalCount();
    for(i = 0; i < nbEvents; i++) {
        fieldData = st.getAt(i);
        var startDate = new Date(fieldData.json.execution_date).clearTime();
        var endDate = new Date(fieldData.json.execution_date).clearTime().add(Date.DAY, 1).add(Date.SECOND, -1);
        var cal_id = 1;
        if(fieldData.json.done)
            cal_id = 2;
        events = events.concat({
            'id': fieldData.json.id,
            'cid': cal_id,
            'title': fieldData.json.title,
            'start': startDate,
            'end': endDate,
            'ad': true,
        });
    }
    var eventData = {
        'evts': events,
    };
    Ext.ns('Ext.charlie');
    Ext.charlie.CalendarData = {
        'calendars': [{
            'id': 1,
            'title': 'Not done',
            'color': 2
        },{
            'id': 2,
            'title': 'Done',
            'color': 26
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
                else {
                    switch(action){
                    case 'create':
                        Ext.charlie.msg('Add', 'Added "' + Ext.value(rec.data[Ext.ensible.cal.EventMappings.Title.name], '(No title)') + '"');
                        break;
                    case 'update':
                        Ext.charlie.msg('Update', 'Updated "' + Ext.value(rec.data[Ext.ensible.cal.EventMappings.Title.name], '(No title)') + '"');
                        break;
                    case 'destroy':
                        Ext.charlie.msg('Delete', 'Deleted "' + Ext.value(rec.data[Ext.ensible.cal.EventMappings.Title.name], '(No title)') + '"');
                        break;
                    }
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
    cal = new Ext.ensible.cal.CalendarPanel({
        id: tester_visa + "_cal",
        activeItem: 2,
        enableEditDetails: false,
        calendarStore: new Ext.charlie.CalendarStore({data: Ext.charlie.CalendarData}),
        eventStore: new Ext.charlie.MemoryEventStore({data: eventData}),
        enableEditDetails: true,
        eventList: eventData,
        title: tester_visa + "'s planning",
        showDayView: false,
        showWeekView: false,
        showMonthView: false,
        multiWeekViewCfg: {
            ddGroup: 'calendarDD',
            user: tester_visa,
            uid: tester_id,
            listeners: {
                'rangeselect': function(cal, dates) {
                    return false;
                }
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
            //'eventclick': function(cal, rec, el) {
                //usersStore.setBaseParam('action', 'usersStore');
                //usersStore.load();
                //return false;
            //},
        },
    });
    return cal;
}
