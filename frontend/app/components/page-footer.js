import Component from '@ember/component';
import Config from 'almanac/config/environment';

export default Component.extend({
  // the default class names for the the component
  classNames: ['footer'],
  version: Config.currentRevision,
  lastUpdatedDate: Config.lastUpdatedDate
});
