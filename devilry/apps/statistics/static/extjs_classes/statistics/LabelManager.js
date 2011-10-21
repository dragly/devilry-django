Ext.define('devilry.statistics.LabelManager', {
    config: {
        loader: undefined
    },
    application_id: 'devilry.statistics.Labels',

    constructor: function(config) {
        this.initConfig(config);
    },
    
    setLabels: function(options) {
        var labelRecords = [];
        Ext.getBody().mask('Updating labels');
        var index = 0;
        this._finished = 0;
        this._watingFor = Ext.Object.getSize(this.loader._students);
        Ext.Object.each(this.loader._students, function(relstudentid, student) {
            var labelspec = Ext.bind(options.callback, options.scope)(student);
            var labelRecord = student.labels[labelspec.labelname];
            var has_label = labelRecord !== undefined; 
            if(labelspec.apply && !has_label) {
                this._createLabel(student, labelspec.labelname, index);
            } else if(!labelspec.apply && has_label) {
                this._deleteLabel(student, labelRecord, index);
            } else {
                this._checkFinished();
            }
            index ++;
        }, this);
    },

    _createLabel: function(student, labelname, index) {
        var record = this._createLabelRecord(student, labelname);
        devilry.extjshelpers.AsyncActionPool.add({
            scope: this,
            callback: function(pool) {
                record.save({
                    scope: this,
                    callback: function(records, op, successful) {
                        Ext.getBody().mask(Ext.String.format('Completed updating label {0}', index));
                        var label = record.get('key');
                        this.loader._students[student.username].labels[label] = record;
                        pool.notifyTaskCompleted();
                        this._checkFinished();
                    }
                });
            }
        });
    },

    _deleteLabel: function(student, record, index) {
        devilry.extjshelpers.AsyncActionPool.add({
            scope: this,
            callback: function(pool) {
                record.destroy({
                    scope: this,
                    callback: function() {
                        Ext.getBody().mask(Ext.String.format('Completed updating label {0}', index));
                        var label = record.get('key');
                        this.loader._students[student.username].labels[label] = undefined;
                        pool.notifyTaskCompleted();
                        this._checkFinished();
                    }
                });
            }
        });
    },

    _checkFinished: function(dontAddToFinished) {
        if(!dontAddToFinished) {
            this._finished ++;
        }
        if(this._watingFor == undefined) {
            return;
        }
        if(this._finished >= this._watingFor) {
            this._watingFor = undefined;
            Ext.getBody().unmask();
            this.loader._onDataChanged();
        }
    },

    _createLabelRecord: function(student, labelname) {
        var record = Ext.create('devilry.apps.administrator.simplified.SimplifiedRelatedStudentKeyValue', {
            relatedstudent: student.relatedstudent.get('id'),
            application: this.application_id,
            key: labelname
        });
        return record;
    },
});
