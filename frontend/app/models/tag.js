import DS from 'ember-data';

const { attr, belongsTo } = DS;

export default DS.Model.extend({
  label: belongsTo('tag-label', { async: true }),
  value: attr('string')
});
