<template>
  <div>
    <!-- Hero Section -->
    <section class="relative pt-32 pb-20 lg:pt-40 lg:pb-24">
      <!-- Background -->
      <div class="absolute inset-0 bg-surface-950" />
      <div class="absolute inset-0 bg-gradient-radial-top" />
      
      <div class="relative container-wide">
        <div class="max-w-2xl mx-auto text-center">
          <UiBadge variant="primary" class="mb-6">Pricing</UiBadge>
          <h1 class="text-3xl sm:text-4xl lg:text-5xl font-mono tracking-tight text-balance mb-4">
            Simple, <span class="gradient-text">transparent</span> pricing
          </h1>
          <p class="text-lg text-surface-400 leading-relaxed font-mono">
            Choose the plan that's right for your business. All plans include a 14-day free trial.
          </p>
        </div>
      </div>
    </section>

    <!-- Pricing Cards -->
    <section class="py-12 md:py-16">
      <div class="container-wide">
        <!-- Divider -->
        <div class="section-divider mb-12" />
        
        <div class="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <!-- Starter -->
          <div class="card p-8">
            <h3 class="text-lg font-mono text-surface-50 mb-2">Starter</h3>
            <p class="text-surface-500 text-sm mb-6 font-mono">For small businesses getting started</p>
            <div class="mb-6">
              <span class="text-4xl font-mono text-surface-50">$29</span>
              <span class="text-surface-500 font-mono">/month</span>
            </div>
            <ul class="space-y-3 mb-8">
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>10 videos per month</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>2 social accounts</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Basic analytics</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Email support</span>
              </li>
            </ul>
            <UiButton variant="secondary" full-width>Get Started</UiButton>
          </div>

          <!-- Pro -->
          <div class="card p-8 border-primary-500/30 relative">
            <div class="absolute -top-3 left-1/2 -translate-x-1/2">
              <UiBadge variant="accent">Most Popular</UiBadge>
            </div>
            <h3 class="text-lg font-mono text-surface-50 mb-2">Pro</h3>
            <p class="text-surface-500 text-sm mb-6 font-mono">For growing businesses</p>
            <div class="mb-6">
              <span class="text-4xl font-mono text-surface-50">$79</span>
              <span class="text-surface-500 font-mono">/month</span>
            </div>
            <ul class="space-y-3 mb-8">
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>50 videos per month</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>5 social accounts</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Advanced analytics</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>AI strategy generation</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Priority support</span>
              </li>
            </ul>
            <UiButton variant="accent" full-width>Get Started</UiButton>
          </div>

          <!-- Enterprise -->
          <div class="card p-8">
            <h3 class="text-lg font-mono text-surface-50 mb-2">Enterprise</h3>
            <p class="text-surface-500 text-sm mb-6 font-mono">For larger teams</p>
            <div class="mb-6">
              <span class="text-4xl font-mono text-surface-50">Custom</span>
            </div>
            <ul class="space-y-3 mb-8">
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Unlimited videos</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Unlimited accounts</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Custom integrations</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>Dedicated manager</span>
              </li>
              <li class="flex items-center gap-2 text-sm text-surface-400 font-mono">
                <UiIcon name="Check" :size="16" class="text-primary-400" />
                <span>SLA guarantee</span>
              </li>
            </ul>
            <UiButton variant="secondary" full-width>Contact Sales</UiButton>
          </div>
        </div>
        
        <!-- Divider -->
        <div class="section-divider mt-12" />
      </div>
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
