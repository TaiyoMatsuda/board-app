<template>
  <div class="event">
    <h1>This is an event page</h1>
    <BaseEvent />
    <ParticipantList />
    <EventCommentList />
  </div>
</template>

<script>
import BaseEvent from '@/components/Event/BaseEvent.vue'
import ParticipantList from '@/components/Participant/ParticipantList.vue'
import EventCommentList from '@/components/EventComment/EventCommentList.vue'

export default {
  name: 'Event',
  components: {
    BaseEvent,
    ParticipantList,
    EventCommentList
  }
}
</script>
