import DS from 'ember-data';

const { attr, belongsTo } = DS;

export default DS.Model.extend({
  value: attr('string'),
  note: attr('string'),

  code_type: belongsTo('code-type', { async: true })
});
