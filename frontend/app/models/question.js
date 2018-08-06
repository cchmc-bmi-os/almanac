import DS from 'ember-data';

const { attr, hasMany } = DS;

export default DS.Model.extend({
  name: attr('string'),

  definitions: hasMany('definition', { async: true }),
  conditions: hasMany('condition', { async: true }),
  codes: hasMany('codes', { async: true })
});
