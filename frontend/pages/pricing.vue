<template>
  <div>
    <!-- Hero Section -->
    <section class="relative overflow-hidden pt-32 pb-20 lg:pt-40 lg:pb-28">
      <!-- Background -->
      <div class="absolute inset-0 bg-surface-900" />
      <div class="absolute inset-0 bg-gradient-radial-top" />
      <div class="absolute top-1/3 left-1/3 w-[400px] h-[400px] bg-primary-500/8 rounded-full blur-[150px]" />
      
      <div class="relative container-wide">
        <div class="max-w-3xl mx-auto text-center">
          <UiBadge variant="primary" class="mb-6">Pricing</UiBadge>
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-display font-bold tracking-tight text-balance mb-6">
            Simple, <span class="gradient-text">Transparent</span> Pricing
          </h1>
          <p class="text-xl text-surface-400 max-w-2xl mx-auto">
            Choose the plan that's right for your business. All plans include a 14-day free trial.
          </p>
        </div>
      </div>
      
      <div class="absolute bottom-0 left-0 right-0 section-divider" />
    </section>

    <!-- Pricing Cards -->
    <section class="section bg-surface-800/30 relative">
      <div class="absolute top-0 left-0 right-0 section-divider" />
      
      <div class="container-wide">
        <div class="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <!-- Starter -->
          <UiCard class="p-8">
            <h3 class="text-lg font-display font-semibold text-surface-100 mb-2">Starter</h3>
            <p class="text-surface-400 text-sm mb-6">Perfect for small businesses just getting started</p>
            <div class="mb-6">
              <span class="text-4xl font-display font-bold text-surface-100">$29</span>
              <span class="text-surface-400">/month</span>
            </div>
            <ul class="space-y-3 mb-8">
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>10 videos per month</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>2 social accounts</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Basic analytics</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Email support</span>
              </li>
            </ul>
            <UiButton variant="secondary" full-width>Get Started</UiButton>
          </UiCard>

          <!-- Pro -->
          <UiCard class="p-8 border-primary-500/50 relative">
            <div class="absolute -top-3 left-1/2 -translate-x-1/2">
              <UiBadge variant="accent">Most Popular</UiBadge>
            </div>
            <h3 class="text-lg font-display font-semibold text-surface-100 mb-2">Pro</h3>
            <p class="text-surface-400 text-sm mb-6">For growing businesses that need more</p>
            <div class="mb-6">
              <span class="text-4xl font-display font-bold text-surface-100">$79</span>
              <span class="text-surface-400">/month</span>
            </div>
            <ul class="space-y-3 mb-8">
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>50 videos per month</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>5 social accounts</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Advanced analytics</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>AI strategy generation</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Priority support</span>
              </li>
            </ul>
            <UiButton variant="accent" full-width>Get Started</UiButton>
          </UiCard>

          <!-- Enterprise -->
          <UiCard class="p-8">
            <h3 class="text-lg font-display font-semibold text-surface-100 mb-2">Enterprise</h3>
            <p class="text-surface-400 text-sm mb-6">For larger teams with custom needs</p>
            <div class="mb-6">
              <span class="text-4xl font-display font-bold text-surface-100">Custom</span>
            </div>
            <ul class="space-y-3 mb-8">
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Unlimited videos</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Unlimited social accounts</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Custom integrations</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Dedicated account manager</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-300">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>SLA guarantee</span>
              </li>
            </ul>
            <UiButton variant="secondary" full-width>Contact Sales</UiButton>
          </UiCard>
        </div>
      </div>
      
      <div class="absolute bottom-0 left-0 right-0 section-divider" />
    </section>

    <!-- CTA -->
    <LandingCTA />
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Pricing - ElevoAI',
  description: 'Simple, transparent pricing for ElevoAI. Choose the plan that\'s right for your business.',
})
</script>
