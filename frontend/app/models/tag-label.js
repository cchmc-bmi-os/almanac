import DS from 'ember-data';

const { attr } = DS;

export default DS.Model.extend({
  label: attr('string'),
  type: attr('string'),
  description: attr('string')
});
