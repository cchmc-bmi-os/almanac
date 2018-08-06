import { get } from '@ember/object';
import Config from 'almanac/config/environment';

export default function isReviewAdmin(session, store) {
  let userId = get(session, 'data.authenticated.user_id');
  return store.query('review-role', { user__id: userId }).then((roles) => {
    let isAdmin = false;

    // see if the user is a member of is admin
    roles.forEach((role) => {
      if (!Config.review.admin) {
        throw new Error('Please specify review admin in the config');
      }

      if ([Config.review.admin].indexOf(role.get('role')) !== -1) {
        isAdmin = true;
      }
    });

    return isAdmin;
  });
}
