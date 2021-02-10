<template>
  <div class="create_update_event">
    <h1>This is a create and update event page</h1>
    <BaseEvent />
  </div>
</template>

<script>
import BaseEvent from '@/components/Event/BaseEvent.vue'

export default {
  name: 'Event',
  components: {
    BaseEvent,
  }
}
</script>
