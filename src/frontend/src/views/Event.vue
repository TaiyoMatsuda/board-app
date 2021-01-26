<template>
  <div class="event">
    <h1>This is an event page</h1>
    <BaseEvent />
    <ParticipantList />
  </div>
</template>

<script>
import BaseEvent from '@/components/Event/BaseEvent.vue'
import ParticipantList from '@/components/Participant/ParticipantList.vue'

export default {
  name: 'Event',
  components: {
    BaseEvent,
    ParticipantList
  }
}
</script>
