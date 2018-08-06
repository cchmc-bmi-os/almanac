import { computed } from '@ember/object';
import DS from 'ember-data';

const { attr } = DS;

export default DS.Model.extend({
  username: attr('string'),
  first_name: attr('string'),
  last_name: attr('string'),
  email: attr('string'),

  fullname: computed('first_name', 'last_name', {
    get() {
      return `${this.get('first_name')} ${this.get('last_name')}`;
    }
  })
});
