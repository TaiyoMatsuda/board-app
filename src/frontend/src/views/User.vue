<template>
  <div class="user">
    <h1>This is user page</h1>
    <ReadUser />
    <JoinedEvent />
    <OrganizedEvent />
  </div>
</template>

<script>
import ReadUser from '@/components/User/ReadUser.vue'
import JoinedEvent from '@/components/User/UserJoinedEvent.vue'
import OrganizedEvent from '@/components/User/UserOrganizedEvent.vue'

export default {
  name: 'User',
  components: {
    ReadUser,
    JoinedEvent,
    OrganizedEvent
  }
}
</script>
