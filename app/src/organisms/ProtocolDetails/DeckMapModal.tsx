import * as React from 'react'
import { useTranslation } from 'react-i18next'

import {
  Flex,
  DIRECTION_COLUMN,
  TYPOGRAPHY,
  SPACING,
  ALIGN_FLEX_END,
} from '@opentrons/components'

import { Portal } from '../../App/portal'
import { Modal } from '../../molecules/Modal'
import { DeckThumbnail } from '../../molecules/DeckThumbnail'
import { PrimaryButton } from '../../atoms/buttons'

import type { RunTimeCommand } from '@opentrons/shared-data'

interface DeckMapModalProps {
  onCloseClick: () => unknown
  protocolType: RunTimeCommand[]
}

export function DeckMapModal({
  onCloseClick,
  protocolType,
}: DeckMapModalProps): JSX.Element {
  const { t } = useTranslation(['protocol_setup', 'shared'])
  return (
    <Portal level="top">
      <Modal title={t('deck_setup')} onClose={onCloseClick} maxHeight="32rem">
        <Flex flexDirection={DIRECTION_COLUMN}>
          <DeckThumbnail commands={protocolType} showLiquids />
          <PrimaryButton
            marginTop={SPACING.spacing4}
            onClick={onCloseClick}
            alignSelf={ALIGN_FLEX_END}
            textTransform={TYPOGRAPHY.textTransformCapitalize}
          >
            {t('shared:close')}
          </PrimaryButton>
        </Flex>
      </Modal>
    </Portal>
  )
}
