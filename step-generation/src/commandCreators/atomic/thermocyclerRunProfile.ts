import type { TCProfileParams } from '@opentrons/shared-data/protocol/types/schemaV4'
import type { CommandCreator } from '../../types'
export const thermocyclerRunProfile: CommandCreator<TCProfileParams> = (
  args,
  invariantContext,
  prevRobotState
) => {
  const { module, profile, volume } = args
  return {
    commands: [
      {
        commandType: 'thermocycler/runProfile',
        params: {
          moduleId: module,
          profile,
          volume,
        },
      },
    ],
  }
}
