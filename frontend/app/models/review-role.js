import DS from 'ember-data';

const { attr, belongsTo } = DS;

export default DS.Model.extend({
  role: attr('string'),
  user: belongsTo('user', { async: true })
});
