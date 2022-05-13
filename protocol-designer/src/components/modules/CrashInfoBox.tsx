import * as React from 'react'
import { Icon } from '@opentrons/components'
import { KnowledgeBaseLink } from '../KnowledgeBaseLink'
import { i18n } from '../../localization'
import styles from './styles.css'

interface Props {
  showDiagram?: boolean
  magnetOnDeck?: boolean | null
  temperatureOnDeck?: boolean | null
  haeterShakerOnDeck?: boolean | null
}
const HS_LABWARE_TALL_TEXT =
  'Labware taller than 53.7 mm cannot be placed to the left or right of a Heater-Shaker GEN1 module.'
const EIGHT_CHANNEL_TEXT =
  '8-Channel pipettes cannot access slots to the left or right of a Heater-Shaker GEN1 module.'

export function CrashInfoBox(props: Props): JSX.Element {
  const moduleMessage = getCrashableModulesCopy(props) || ''
  return (
    <div className={styles.crash_info_container}>
      <div className={styles.crash_info_box}>
        <div className={styles.crash_info_title}>
          <Icon name="information" className={styles.alert_icon} />
          <strong>Limited access to slots</strong>
        </div>
        <p>
          <strong>GEN1 8-Channel</strong> pipettes cannot access slots behind{' '}
          <strong>GEN1 {moduleMessage} modules.</strong>
        </p>
        {/* if heater shaker present */}
        <p>{HS_LABWARE_TALL_TEXT}</p>
        <p>{EIGHT_CHANNEL_TEXT}</p>
        <KnowledgeBaseLink to="pipetteGen1MultiModuleCollision">
          Read more here
        </KnowledgeBaseLink>
      </div>
      {props.showDiagram && (
        <img
          className={styles.crash_info_diagram}
          // @ts-expect-error(sa, 2021-6-21): src should be string | undefined, null is not cool with TS
          src={getCrashDiagramSrc(props)}
        />
      )}
    </div>
  )
}

function getCrashableModulesCopy(props: Props): string | null {
  const { magnetOnDeck, temperatureOnDeck } = props
  if (magnetOnDeck && temperatureOnDeck) {
    return 'Temperature or Magnetic'
  } else if (magnetOnDeck) {
    return 'Magnetic'
  } else if (temperatureOnDeck) {
    return 'Temperature'
  }
  return null
}
function getCrashDiagramSrc(props: Props): string | null {
  const { magnetOnDeck, temperatureOnDeck } = props
  const CRASH_DIAGRAM_SRC: string | null = null
  if (magnetOnDeck && temperatureOnDeck) {
    return require('../../images/modules/crash_warning_mag_temp.png')
  } else if (magnetOnDeck) {
    return require('../../images/modules/crash_warning_mag.png')
  } else if (temperatureOnDeck) {
    return require('../../images/modules/crash_warning_temp.png')
  }
  return CRASH_DIAGRAM_SRC
}
