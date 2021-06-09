// @flow
import * as React from 'react'
import cx from 'classnames'
import { Tooltip, useHoverTooltip, TOOLTIP_FIXED } from '@opentrons/components'
import { PDListItem } from '../lists'
import styles from './StepItem.css'
import { LabwareTooltipContents } from './LabwareTooltipContents'

type Props = {
  volume: string | null | undefined
  times: string | null | undefined
  labwareNickname: string | null | undefined
}

export function MixHeader(props: Props): React.Node {
  const { volume, times, labwareNickname } = props
  const [targetProps, tooltipProps] = useHoverTooltip({
    placement: 'bottom-start',
    strategy: TOOLTIP_FIXED,
  })
  return (
    <>
      <Tooltip {...tooltipProps}>
        <LabwareTooltipContents {...{ labwareNickname }} />
      </Tooltip>

      <PDListItem className={styles.step_subitem}>
        <span
          {...targetProps}
          className={cx(styles.emphasized_cell, styles.labware_display_name)}
        >
          {labwareNickname}
        </span>

        <span>{volume} uL</span>
        <span>{times}x</span>
      </PDListItem>
    </>
  )
}