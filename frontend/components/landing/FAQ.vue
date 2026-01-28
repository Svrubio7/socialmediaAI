<template>
  <section id="faq" class="section bg-surface-900 relative">
    <!-- Top divider -->
    <div class="absolute top-0 left-0 right-0 section-divider" />
    
    <div class="container-tight">
      <!-- Section Header -->
      <div class="text-center max-w-2xl mx-auto mb-16">
        <UiBadge variant="primary" class="mb-4">{{ $t('faq.badge') }}</UiBadge>
        <h2 class="text-3xl sm:text-4xl font-display font-bold text-balance mb-6">
          {{ $t('faq.title') }}
        </h2>
        <p class="text-lg text-surface-400">
          {{ $t('faq.subtitle') }}
        </p>
      </div>

      <!-- FAQ Items -->
      <div class="space-y-4">
        <div 
          v-for="(item, index) in faqs" 
          :key="index"
          class="border border-surface-700 rounded-2xl overflow-hidden bg-surface-800/50"
        >
          <button
            class="w-full flex items-center justify-between p-6 text-left hover:bg-surface-700/30 transition-colors"
            @click="toggleFaq(index)"
          >
            <span class="font-display font-semibold text-surface-100 pr-4">
              {{ $t(item.questionKey) }}
            </span>
            <UiIcon 
              name="ChevronDown" 
              :size="20" 
              class="text-surface-400 flex-shrink-0 transition-transform duration-200"
              :class="{ 'rotate-180': openIndex === index }"
            />
          </button>
          
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 -translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-2"
          >
            <div v-if="openIndex === index" class="px-6 pb-6">
              <p class="text-surface-400 leading-relaxed">
                {{ $t(item.answerKey) }}
              </p>
            </div>
          </Transition>
        </div>
      </div>
    </div>
    
    <!-- Bottom divider -->
    <div class="absolute bottom-0 left-0 right-0 section-divider" />
  </section>
</template>

<script setup lang="ts">
const openIndex = ref<number | null>(0)

const toggleFaq = (index: number) => {
  openIndex.value = openIndex.value === index ? null : index
}

const faqs = [
  { questionKey: 'faq.q1', answerKey: 'faq.a1' },
  { questionKey: 'faq.q2', answerKey: 'faq.a2' },
  { questionKey: 'faq.q3', answerKey: 'faq.a3' },
  { questionKey: 'faq.q4', answerKey: 'faq.a4' },
  { questionKey: 'faq.q5', answerKey: 'faq.a5' },
  { questionKey: 'faq.q6', answerKey: 'faq.a6' },
]
</script>
