import DS from 'ember-data';

const { attr } = DS;

export default DS.Model.extend({
  help_email: attr('string'),
  help_email_text: attr('string'),
  help_email_subject: attr('string')
});
