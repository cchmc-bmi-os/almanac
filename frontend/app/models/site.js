import DS from 'ember-data';

const { attr } = DS;

export default DS.Model.extend({
  name: attr('string'),
  display: attr('string'),
  pi: attr('string'),
  live: attr('boolean')
});
