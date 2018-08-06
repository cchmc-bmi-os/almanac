/* jshint node: true */

module.exports = function(deployTarget) {
  let ENV = {
    build: {}
    // include other plugin configuration that applies to all deploy targets here
  };

  if (deployTarget === 'development') {
    ENV.build.environment = 'dev-lpdr';
    // configure other plugins for development deploy target here
    ENV.rsync = {
      type: 'rsync',
      dest: '/var/www/almanac/frontend/dist',
      host: 'bmilpdralmd2.chmcres.cchmc.org',
      ssh: true,
      recursive: true,
      delete: true,
      args: ['-ztl']
    };
  }

  if (deployTarget === 'testing') {
    ENV.build.environment = 'test-lpdr';
    // configure other plugins for staging deploy target here
    ENV.rsync = {
      type: 'rsync',
      dest: '/var/www/almanac/frontend/dist',
      host: 'bmilpdralms1.chmcres.cchmc.org',
      ssh: true,
      recursive: true,
      delete: true,
      args: ['-ztl']
    };
  }

  if (deployTarget === 'bmilpdralmt1') {
    ENV.build.environment = 'bmilpdralmt1';
    // configure other plugins for development deploy target here
    ENV.rsync = {
      type: 'rsync',
      dest: '/var/www/almanac/frontend/dist',
      host: 'bmilpdralmt1.chmcres.cchmc.org',
      ssh: true,
      recursive: true,
      delete: true,
      args: ['-ztl']
    };
  }

  if (deployTarget === 'production') {
    ENV.build.environment = 'production';
    // configure other plugins for production deploy target here
    ENV.rsync = {
      type: 'rsync',
      dest: '/var/www/almanac/frontend/dist',
      host: 'bmilpdralmp1.chmcres.cchmc.org',
      ssh: true,
      recursive: true,
      delete: true,
      args: ['-ztl']
    };
  }

  // Note: if you need to build some configuration asynchronously, you can return
  // a promise that resolves with the ENV object instead of returning the
  // ENV object synchronously.
  return ENV;
};
