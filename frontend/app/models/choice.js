import DS from 'ember-data';

const { attr, hasMany } = DS;

export default DS.Model.extend({
  text: attr('string'),
  value: attr('string'),

  definitions: hasMany('definition', { async: true })
});
