export function getMetaData(error, container) {
  let currentUser = container.lookup('service:current-user');

  return {
    user: {
      name: currentUser.get('fullname'),
      username: currentUser.get('user.username'),
      email: currentUser.get('user.email')
    }
  };
}
