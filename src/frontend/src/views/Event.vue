<template>
  <div class="event">
    <h1>This is an event page</h1>
    <router-link :to="{ name: 'CreateUpdateEvent', query: { id: this.$route.query.id}}">
      edit
    </router-link>
    <BaseEvent />
    <BaseParticipant />
    <BaseEventComment />
  </div>
</template>

<script>
import BaseEvent from '@/components/Event/BaseEvent.vue'
import BaseParticipant from '@/components/Participant/BaseParticipant.vue'
import BaseEventComment from '@/components/EventComment/BaseEventComment.vue'

export default {
  name: 'Event',
  components: {
    BaseEvent,
    BaseParticipant,
    BaseEventComment,
  },
}
</script>
