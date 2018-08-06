'use strict';

module.exports = function(environment) {
  let ENV = {
    modulePrefix: 'almanac',
    environment,
    rootURL: '/',
    locationType: 'auto',
    currentRevision: '2.2.0',
    lastUpdatedDate: '2018-08-02',
    review: {
      roles: ['CCHMC', 'ACMG'],
      admin: 'CCHMC'
    },
    bugsnag: {
      apiKey: '88ecc21bbf7d046198b170139905b7d8',
      notifyReleaseStages: ['dev-lpdr', 'test-lpdr', 'prod-lpdr'],
      releaseStage: environment,
      endpoint: 'https://bugsnag-notify.research.cchmc.org/js'
    },
    moment: {
      outputFormat: 'MM/DD/YYYY h:mm A'
    },
    EmberENV: {
      FEATURES: {
        // Here you can enable experimental features on an ember canary build
        // e.g. 'with-controller': true
      },
      EXTEND_PROTOTYPES: {
        // Prevent Ember Data from overriding Date.parse.
        Date: false
      }
    },

    APP: {
      // Here you can pass flags/options to your application instance
      // when it is created
    }
  };

  if (environment === 'development') {
    // ENV.APP.LOG_RESOLVER = true;
    // ENV.APP.LOG_ACTIVE_GENERATION = true;
    // ENV.APP.LOG_TRANSITIONS = true;
    // ENV.APP.LOG_TRANSITIONS_INTERNAL = true;
    // ENV.APP.LOG_VIEW_LOOKUPS = true;

    ENV.api = {
      namespace: 'api/v1',
      host: 'http://localhost:8000',
      auth: 'auth',
      refresh: 'refresh'
    }

    ENV['ember-cli-mirage'] = {
      enabled: false
    };
  }

  if (environment === 'test') {
    // Testem prefers this...
    ENV.locationType = 'none';

    // keep test console output quieter
    ENV.APP.LOG_ACTIVE_GENERATION = false;
    ENV.APP.LOG_VIEW_LOOKUPS = false;

    ENV.APP.rootElement = '#ember-testing';
    ENV.APP.autoboot = false;

    ENV.api = {
      namespace: 'api/v1',
      host: 'http://localhost:8000',
      auth: 'auth',
      refresh: 'refresh'
    }
  }

  if (environment === 'dev-lpdr') {
    ENV.rootURL = '/almanac/';

    ENV.api = {
      namespace: 'almanac/api/v1',
      host: 'https://lpdrdev.research.cchmc.org',
      auth: 'auth',
      refresh: 'refresh'
    };

    ENV['ember-cli-mirage'] = {
      enabled: false
    };
  }

  if (environment === 'test-lpdr') {
    ENV.rootURL = '/almanac/';

    ENV.api = {
      namespace: 'almanac/api/v1',
      host: 'https://lpdr-test.research.cchmc.org',
      auth: 'auth',
      refresh: 'refresh'
    };

    ENV['ember-cli-mirage'] = {
      enabled: false
    };
  }

  if (environment === 'bmilpdralmt1') {
    ENV.rootURL = '/almanac/';

    ENV.api = {
      namespace: 'almanac/api/v1',
      host: 'http://bmilpdralmt1.chmcres.cchmc.org',
      auth: 'auth',
      refresh: 'refresh'
    };

    ENV['ember-cli-mirage'] = {
      enabled: false
    };
  }

  if (environment === 'production') {
    ENV.rootURL = '/almanac/';

    ENV.api = {
      namespace: 'almanac/api/v1',
      host: 'https://lpdr.nbstrn.org',
      auth: 'auth',
      refresh: 'refresh'
    };

    ENV['ember-cli-mirage'] = {
      enabled: false
    };
  }

  return ENV;
};
