import * as React from 'react'
import { connect } from 'react-redux'
import { FeatureFlagCard as FeatureFlagCardComponent } from './FeatureFlagCard'
import {
  actions as featureFlagActions,
  selectors as featureFlagSelectors,
} from '../../../feature-flags'
import { Dispatch } from 'redux'
import { ElementProps } from 'react'
import { BaseState } from '../../../types'
type Props = ElementProps<typeof FeatureFlagCardComponent>
type SP = {
  flags: Props['flags']
}
type DP = {
  setFeatureFlags: Props['setFeatureFlags']
}

const mapStateToProps = (state: BaseState): SP => ({
  flags: featureFlagSelectors.getFeatureFlagData(state),
})

const mapDispatchToProps = (dispatch: Dispatch<any>): DP => ({
  setFeatureFlags: flags => dispatch(featureFlagActions.setFeatureFlags(flags)),
})

export const FeatureFlagCard: React.AbstractComponent<{}> = connect<
  Props,
  {},
  SP,
  DP,
  BaseState,
  _
>(
  mapStateToProps,
  mapDispatchToProps
)(FeatureFlagCardComponent)