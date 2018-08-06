import { computed } from '@ember/object';
import DS from 'ember-data';

const { attr } = DS;

export default DS.Model.extend({
  label: attr('string'),
  name: attr('string'),
  ordering: attr('number'),

  display: computed('name', {
    get() {
      return this.get('name');
    }
  })
});
