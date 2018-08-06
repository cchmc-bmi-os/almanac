import $ from 'jquery';
import Component from '@ember/component';
import { computed, get } from '@ember/object';
import { isEmpty } from '@ember/utils';
import { run } from '@ember/runloop';
import Config from 'almanac/config/environment';
import { task, timeout } from 'ember-concurrency';
import { A } from '@ember/array';

export default Component.extend({
  classNames: ['data-element'],
  cdeActions: 1,
  review: false,
  showActions: false,
  lookup: computed({
    get() {
      return {
        0: 'name',
        1: 'form',
        2: 'section',
        3: 'type',
        4: 'text',
        5: 'choices',
        6: 'note',
        7: 'validation',
        8: 'min_val',
        9: 'max_val',
        10: 'identifier',
        11: 'branching_logic',
        12: 'required',
        13: 'align',
        14: 'order_number',
        15: 'matrix_name',
        16: 'matrix_ranking'
      };
    }
  }),
  types: A([
    { id: 'integer', text: 'Integer' },
    { id: 'text', text: 'Text' },
    { id: 'checkbox', text: 'Checkbox' },
    { id: 'yesno', text: 'Yes/No' },
    { id: 'dropdown', text: 'Dropdown' },
    { id: 'date_mdy', text: 'Date: MM/DD/YYYY' },
    { id: 'date_dmy', text: 'Date: DD/MM/YYYY' },
    { id: 'date_ymd', text: 'Date: YYYYY/MM/DD' },
    { id: 'datetime_mdy', text: 'Datetime: MM/DD/YYYY HH:MM' },
    { id: 'datetime_dmy', text: 'Datetime: DD/MM/YYYY HH:MM' },
    { id: 'datetime_ymd', text: 'Datetime: YYYY/MM/DD HH:MM' },
    { id: 'datetime_seconds_mdy', text: 'Datetime with seconds: MM/DD/YYYY HH:MM:SS' },
    { id: 'datetime_seconds_dmy', text: 'Datetime with seconds: DD/MM/YYYY HH:MM:SS' },
    { id: 'datetime_seconds_ymd', text: 'Datetime with seconds: YYYY/MM/DD HH:MM:SS' },
    { id: 'email', text: 'Email' },
    { id: 'alpha_only', text: 'Letters Only' },
    { id: 'mrn_10d', text: 'MRN {10 digits)' },
    { id: 'number', text: 'Number' },
    { id: 'number_1dp', text: 'Number with 1 Decimal Place' },
    { id: 'number_2dp', text: 'Number with 2 Decimal Place' },
    { id: 'number_3dp', text: 'Number with 3 Decimal Place' },
    { id: 'number_4dp', text: 'Number with 4 Decimal Place' },
    { id: 'phone_australia', text: 'Phone - Australia' },
    { id: 'phone', text: 'Phone' },
    { id: 'postalcode_australia', text: 'Postal Code - Australia' },
    { id: 'postalcode_canada', text: 'Postal Code - Canada' },
    { id: 'ssn', text: 'Social Security Number - U.S.' },
    { id: 'time', text: 'Time: HH:MM' },
    { id: 'time_mm_ss', text: 'Time: MM:SS' },
    { id: 'vmrn', text: 'Vanderbilt MRN' },
    { id: 'zipcode', text: 'Zipcode - U.S.' },
    { id: 'truefalse', text: 'True/False' },
    { id: 'notes', text: 'Note' },
    { id: 'description', text: 'Descipriton' },
    { id: 'sql', text: 'SQL Field' },
    { id: 'radio', text: 'Radio Button' },
    { id: 'calc', text: 'Calculated Field' },
    { id: 'matrix', text: 'Matrix' },
    { id: 'descriptive', text: 'Descriptive' }
  ]),
  allowedOperations: A([
      { id: 'add_existing', text: 'Add a CDE from Data Almanac', summary: '`:additional:` added from Data Almanac :location: `:cde:` (Please verify form and section, and review any branching logic)' },
      { id: 'add_new', text: 'Propose addition to the Data Almanac', summary: '`:cde:` added from reviewer (Please review any branching logic)' },
      { id: 'add_note', text: 'Add a note to the CDE', summary: '`:cde:` with note `:additional:`' },
      { id: 'delete', text: 'Remove the CDE', summary: '`:cde:` has been removed from the Data Dictionary' },
      { id: 'multiples_found', text: 'Flag as a duplicate CDE', summary: '`:cde:` is a duplicate entry' },
      { id: 'update_label', text: 'Update the CDE label', summary: '`:cde:` update label with `:additional:`' },
      { id: 'update_branching', text: 'Update the CDE branching logic', summary: '`:cde:` update branching logic with `:additional:`' },
      { id: 'update_control', text: 'Update the CDE type', summary: '`:cde:` update control type with `:additional:`' },
      { id: 'update_choices', text: 'Update the CDE choices', summary: '`:cde:` update choices with `:additional:`' },
      { id: 'update_da', text: 'Update the Data Almanac with this CDE', summary: '`:cde:` was found and will update CDE in Data Almanac' },
      { id: 'rename', text: 'Rename the CDE', summary: '`:cde:` has been renamed to `:additional:` (Branching logic has been updated)' },
      { id: 'replace', text: 'Replace CDE from Data Almanac', summary: '`:cde:` updated to match CDE in the Data Almanac: `:additional:` (Branching logic has been updated, please check to make sure its correct)' },
      { id: 'tag_condition', text: 'Tag with condition(s)', summary: 'Tagging condition `:additional:` to `:cde:`' }
  ]),
  replaceOperation: computed('allowedOperations', {
    get() {
      return this.get('allowedOperations').filter((op) => {
        return op.id === 'replace';
      })[0];
    }
  }),
  hasAReplaceOperation: computed('cde.operations', {
    get() {
      let operations = this.get('cde.operations');
      let replaceOp = [];

      if (operations) {
        replaceOp = operations.filter((op) => {
          return op.operation === 'replace';
        });
      }

      return replaceOp.length > 0;
    }
  }),
  operationNotAccepted: computed('cde.operations', function() {
    let notAcceptedOperations = this.get('cde.operations').filter((op) => {
      return get(op, 'accepted') === false;
    });

    return notAcceptedOperations.length > 0;
  }),
  cde: computed('data', 'version.actions', 'type', {
    get() {
      let data = (this.get('type') === 'different' || this.get('type') === 'not_found') ? this.get('data.uploaded') : this.get('data');
      let operations = [];
      if (this.get('version.actions')) {
        operations = this.get('version.actions')[data[0]];
      }

      let result = {
        name: data[0],
        form: data[1],
        section: data[2],
        type: data[3],
        text: data[4],
        branching_logic: data[11],
        validation: data[7],
        operations
      };

      if (data[3] === 'calc') {
        result['calculation'] = data[5];
      } else {
        result['choices'] = data[5];
      }

      return result;
    }
  }),

  possible: computed('data', 'type', {
    get() {
      if (this.get('type') === 'different' || this.get('type') === 'not_found') {
        let data = this.get('data');
        if (data.possible) {
          return data.possible;
        }
      }

      return [];
    }
  }),

  differences: computed('data', 'type', {
    get() {
      let differences = {};
      if (this.get('type') === 'different') {
        let data = this.get('data');
        if (data.differences) {
          data.differences.forEach((difference) => {
            let current = (isEmpty(data.uploaded[difference])) ? 'NULL' : data.uploaded[difference];

            let lookupKey = this.get('lookup')[difference];
            if (data.uploaded[3] === 'calc' && lookupKey === 'choices') {
              // switch to calculation and not choices
              lookupKey = 'calculation';
            }
            let dbValue = data.database[lookupKey];
            let original = (isEmpty(dbValue)) ? 'NULL' : dbValue;

            differences[lookupKey] = {
              label: lookupKey,
              current,
              original
            };
          });
        }
      }

      return differences;
    }
  }),
  choices: computed('data', 'type', {
    get() {
      let data = (this.get('type') === 'different') ? this.get('data.uploaded') : this.get('data');
      // let data = this.get('data');
      let choices = [];

      if (data[3] === 'radio' || data[3] === 'dropdown') {
        if (!isEmpty(data[5])) {
          data[5].split('|').forEach((choice) => {
            let parts = choice.split(', ');
            choices.push({
              value: parts[0],
              text: parts[1]
            });
          });
        }
      }

      return choices;
    }
  }),
  other: computed('data', 'type', {
    get() {
      let data = (this.get('type') === 'different' || this.get('type') === 'not_found') ? this.get('data.uploaded') : this.get('data');
      let other = null;
      if (data[3] !== 'radio' && data[3] !== 'dropdown' && !isEmpty(data[5])) {
        other = data[5];
      }

      return other;
    }
  }),

  showAnnotationsButton: computed('review', 'type', 'cde.operations', {
    get() {
      if (this.get('type') === 'found') {
        return false;
      }

      return !this.get('review') || (this.get('review') && this.get('cde.operations.length'));
    }
  }),

  searchCdes: task(function* (term) {
    yield timeout(250);

    let data = yield $.ajax({
      url: `${Config.api.host}/${Config.api.namespace}/questions/typeahead`,
      type: 'GET',
      data: { term },
      dataType: 'json'
    });

    return data;
  }).restartable(),

  didInsertElement() {
    this.set('review', this.get('version.review.status') === 'Grantee Review');
  },

  handleQuestionSelect() {
    this.set('addExistingType', null);
  },
  generateSummary(cde, data) {
    let lookup = this.get('currentOperation.summary');

    lookup = lookup.replace(/:cde:/, cde);
    lookup = lookup.replace(/:additional:/, data.additional);

    if (data.location) {
      lookup = lookup.replace(/:location:/, data.location);
    }

    return lookup;
  },

  showAddBtn: computed('currentOperation', {
    get() {
      let operation = this.get('currentOperation');

      if (this.get('cdeNameError') !== null) {
        return false;
      }

      return isEmpty(operation) ? false : true;
    }
  }),

  cdeNameError: computed('additionalInfo', {
    get() {
      let operation = this.get('currentOperation');
      let additionalInfo = this.get('additionalInfo');
      let renameError = null;

      if (operation.id === 'rename') {
        if (isEmpty(additionalInfo)) {
          renameError = 'Please enter a name';
        } else {
          // enforce lowercase
          additionalInfo = additionalInfo.toLowerCase();

          // make sure it starts with a lowercase character
          if (!additionalInfo[0].match(/[a-z]/)) {
            renameError = 'CDE must start with a letter';
          }

          // make sure non alpha numerics are not allowed
          if (additionalInfo.match(/\W/)) {
            renameError = 'CDE must only contain alphanumeric characters or underscore';
          }

          // make sure only single underscores are used
          if (additionalInfo.match(/__+/)) {
            renameError = 'CDE must only contain single underscores';
          }

          // name length should be a max of 32 characters
          if (additionalInfo.length > 32) {
            renameError = 'CDE must be 32 characters or less';
          }
        }
      }

      return renameError;
    }
  }),

  showTextareaEntry: computed('currentOperation', {
    get() {
      let operation = this.get('currentOperation');
      let actions = [
        'add_note',
        'update_branching',
        'update_choices'
      ];

      return actions.indexOf(operation.id) !== -1;
    }
  }),

  showTextEntry: computed('currentOperation', {
    get() {
      let operation = this.get('currentOperation');
      let actions = [
        'update_label',
        'rename'
      ];

      return actions.indexOf(operation.id) !== -1;
    }
  }),

  showTypeSelect: computed('currentOperation', {
    get() {
      let operation = this.get('currentOperation');
      let actions = [
        'update_control'
      ];

      return actions.indexOf(operation.id) !== -1;
    }
  }),

  showQuestionSelect: computed('currentOperation', {
    get() {
      let operation = this.get('currentOperation');
      let actions = [
        'replace',
        'update_da'
      ];

      return actions.indexOf(operation.id) !== -1;
    }
  }),

  showConditionSelect: computed('currentOperation', {
    get() {
      let operation = this.get('currentOperation');
      let actions = [
        'tag_condition',
      ];

      return actions.indexOf(operation.id) !== -1;
    }
  }),

  actions: {
    toggleActions() {
      this.set('additionalInfo', null);
      this.toggleProperty('showActions');
    },
    updateOperations(cde, value) {
      this.set('currentOperation', value);

      let additionalInfo = null;
      switch (value.id) {
        case 'update_branching':
          additionalInfo = this.get('cde.branching_logic');
          break;
        case 'update_choices':
          additionalInfo = this.get('cde.choices');
          break;
        case 'rename':
          additionalInfo = this.get('cde.name');
          break;
        case 'update_label':
          additionalInfo = this.get('cde.text');
          break;
      }

      this.set('additionalInfo', additionalInfo);
    },
    addOperation() {
      let data = {
        additional: this.get('additionalInfo'),
        operation: this.get('currentOperation.id'),
        accepted: true
      };

      switch (data.operation) {
        case 'update_control':
          data.additional = data.additional.text;
          break;
        case 'add_existing':
          data.location = this.get('addExistingType');
          data.additional = data.additional.name;
          break;
        case 'replace':
          data.additional = data.additional.name;
          break;
      }

      let allNames = [];
      let allData = [];
      let allSummary = [];

      if (data.operation === 'tag_condition') {
        const conditions = data.additional;

        // for each condition
        conditions.forEach((condition) => {
          let newData = {
            additional: condition.get('name'),
            operation: data.operation
          }

          allSummary.push(this.generateSummary(this.get('cde.name'), newData));
          allNames.push(this.get('cde.name'));
          allData.push(newData);
        });
      } else {
        allSummary.push(this.generateSummary(this.get('cde.name'), data));
        allNames.push(this.get('cde.name'));
        allData.push(data);
      }

      // do the add operation(s)
      this.get('add')(allNames, allData, allSummary);

      this.set('currentOperation', null);
      this.set('additionalInfo', null);
    },
    forceReplace(name) {
      let data = {
        additional: name,
        operation: 'replace',
        accepted: true
      };
      this.set('currentOperation', this.get('replaceOperation'));

      let summary = this.generateSummary(this.get('cde.name'), data);

      this.get('add')([this.get('cde.name')], [data], [summary]);

      this.set('currentOperation', null);
    },
    removeOperation(operation) {
      this.get('remove')(this.get('cde.name'), operation);
    },
    toggleClearAllConfirm() {
      this.toggleProperty('showClearAll');
    },
    clearOperations() {
      this.get('clear')(this.get('cde.name'));
      if (this.get('review')) {
        this.send('toggleActions');
      }
      this.send('toggleClearAllConfirm');
    },
    searchCdes(term) {
      return run.debounce(this, 'searchCdes', term, 300);
    }
  }
});
