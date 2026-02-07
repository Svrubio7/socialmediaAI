<template>
  <section id="faq" class="section">
    <div class="container-tight">
      <!-- Section Header -->
      <div 
        ref="headerRef"
        class="text-center max-w-2xl mx-auto mb-12 transition-all duration-700"
        :class="headerVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'"
      >
        <UiBadge variant="primary" class="mb-4">{{ $t('faq.badge') }}</UiBadge>
        <h2 class="text-3xl sm:text-4xl font-mono text-balance mb-4">
          {{ $t('faq.title') }}
        </h2>
        <p class="text-surface-400 leading-relaxed font-mono">
          {{ $t('faq.subtitle') }}
        </p>
      </div>

      <!-- FAQ Items with staggered animation -->
      <div class="space-y-3 max-w-2xl mx-auto">
        <div 
          v-for="(item, index) in faqs" 
          :key="index"
          ref="faqRefs"
          class="border border-surface-800 rounded-xl overflow-hidden bg-surface-900 transition-all duration-500"
          :class="visibleFaqs[index] ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
          :style="{ transitionDelay: `${index * 75}ms` }"
        >
          <button
            class="w-full flex items-center justify-between p-5 text-left hover:bg-surface-800 transition-colors"
            @click="toggleFaq(index)"
          >
            <span class="text-surface-100 pr-4 font-mono">
              {{ $t(item.questionKey) }}
            </span>
            <UiIcon 
              name="ChevronDown" 
              :size="18" 
              class="text-surface-500 flex-shrink-0 transition-transform duration-200"
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
            <div v-if="openIndex === index" class="px-5 pb-5">
              <p class="text-surface-400 text-sm leading-relaxed font-mono">
                {{ $t(item.answerKey) }}
              </p>
            </div>
          </Transition>
        </div>
      </div>
      
      <!-- Contained divider -->
      <div class="section-divider mt-12" />
    </div>
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

const headerRef = ref<HTMLElement | null>(null)
const faqRefs = ref<HTMLElement[]>([])
const headerVisible = ref(false)
const visibleFaqs = ref<boolean[]>(new Array(faqs.length).fill(false))

onMounted(() => {
  // Header observer
  const headerObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          headerVisible.value = true
          headerObserver.disconnect()
        }
      })
    },
    { threshold: 0.2 }
  )
  
  if (headerRef.value) {
    headerObserver.observe(headerRef.value)
  }
  
  // FAQ items observer
  const faqObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const index = faqRefs.value.indexOf(entry.target as HTMLElement)
          if (index !== -1) {
            visibleFaqs.value[index] = true
          }
        }
      })
    },
    { 
      threshold: 0.1,
      rootMargin: '0px 0px -30px 0px'
    }
  )
  
  faqRefs.value.forEach((el) => {
    if (el) faqObserver.observe(el)
  })
  
  onUnmounted(() => {
    headerObserver.disconnect()
    faqObserver.disconnect()
  })
})
</script>
