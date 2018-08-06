import { computed } from '@ember/object';
import RSVP from 'rsvp';
import DS from 'ember-data';

const { attr, belongsTo, hasMany } = DS;

export default DS.Model.extend({
  align: attr('string'),
  branching_logic: attr('string'),
  calculation: attr('string'),
  matrix_name: attr('string'),
  max_val: attr('string'),
  min_val: attr('string'),
  name: attr('string'),
  note: attr('string'),
  ordering: attr('number'),
  text: attr('string'),
  type: attr('string'),
  unknown_val: attr('string'),

  question: belongsTo('question', { async: true }),
  sites: belongsTo('site', { async: true }),
  form: belongsTo('form', { async: true }),
  choices: hasMany('choice', { async: true }),
  tags: hasMany('tag', { async: true }),

  classification: computed('tags', {
    get() {
      let tags = this.get('tags');
      let classification = null;

      if (tags.length) {
        let reqs = [];

        tags.forEach((tag) => {
          reqs.pushObject(tag.get('label'));
        });

        RSVP.all(reqs).then(() => {
          tags.forEach((tag) => {
            if (tag.get('label.label') === 'Classification') {
              this.set('classification', tag.get('value'));
              classification = tag.get('value');
            }
          });
        });
      }

      return classification;
    }
  })
});
