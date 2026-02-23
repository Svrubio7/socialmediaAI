export type TimelineTransitionType = 'cross_fade' | 'hard_wipe'

export interface TimelineTransition {
  id: string
  type: TimelineTransitionType
  fromClipId: string
  toClipId: string
  group: 'video'
  layer: number
  durationFrames: number
  direction?: 'left' | 'right' | 'up' | 'down'
}
