import { getLabwareDisplayName } from '.'
import { PickUpTipCommand } from '../../protocol/types/schemaV6/command/pipetting'
import type { LoadLabwareCommand } from '../../protocol/types/schemaV6/command/setup'
import type { Command, ProtocolFile } from '../../protocol'
import type { PipetteName } from '../pipettes'
import type { ProtocolResource, LabwareDefinition2 } from '../types'
// This adapter exists to resolve the interface mismatch between the PE analysis response
// and the protocol schema v6 interface. Much of this logic should be deleted once we resolve
// these discrepencies on the server side
export const schemaV6Adapter = (
  protocolAnalyses: ProtocolResource['analyses'][0]
): ProtocolFile<{}> => {
  if (protocolAnalyses != null && protocolAnalyses.status === 'completed') {
    const pipettes: {
      [pipetteId: string]: { name: PipetteName }
    } = protocolAnalyses.pipettes.reduce((acc, pipette) => {
      return {
        ...acc,
        [pipette.id]: {
          name: pipette.pipetteName,
        },
      }
    }, {})

    const labware: {
      [labwareId: string]: {
        definitionId: string
        displayName?: string
      }
    } = protocolAnalyses.labware.reduce((acc, labware) => {
      const labwareId = labware.id
      if (labwareId === 'fixedTrash') {
        return { ...acc }
      }
      const labwareDef: LabwareDefinition2 = protocolAnalyses.commands.find(
        (command: Command) =>
          command.commandType === 'loadLabware' &&
          command.result?.labwareId === labwareId
      )?.result.definition

      return {
        ...acc,
        [labwareId]: {
          definitionId: `${labware.definitionUri}_id`,
          displayName: getLabwareDisplayName(labwareDef),
        },
      }
    }, {})

    const labwareDefinitions: {
      [definitionId: string]: LabwareDefinition2
    } = protocolAnalyses.commands
      .filter(
        (command: Command): command is LoadLabwareCommand =>
          command.commandType === 'loadLabware'
      )
      .reduce((acc, command: LoadLabwareCommand) => {
        // @ts-expect-error at the time this adapter is being used the commands should all be resolved
        const labwareDef: LabwareDefinition2 = command.result?.definition
        const labwareId = command.result?.labwareId ?? ''
        const definitionUri = protocolAnalyses.labware.find(
          labware => labware.id === labwareId
        )?.definitionUri
        const definitionId = `${definitionUri}_id`

        return {
          ...acc,
          [definitionId]: labwareDef,
        }
      }, {})

    // This is a temporary hack that should be deleted as soon as pickup tip command mapping is implemented in protocol engine
    const commands = protocolAnalyses.commands.map((command, index) => {
      if (command.id.includes('PICK_UP_TIP')) {
        const shimmedPickupTipCommand: PickUpTipCommand = {
          id: index.toString(),
          commandType: 'pickUpTip',
          params: {
            pipetteId: index % 2 === 0 ? 'pipette-0' : 'pipette-1',
            labwareId: index % 2 === 0 ? 'labware-1' : 'labware-3',
            wellName: 'A1',
          },
          result: {
            pipetteId: index % 2 === 0 ? 'pipette-0' : 'pipette-1',
            labwareId: index % 2 === 0 ? 'labware-1' : 'labware-3',
          },
        }
        return shimmedPickupTipCommand
      }
      return command
    })

    // @ts-expect-error this is a v6 like object that does not quite match the v6 spec at the moment
    return {
      pipettes,
      labware,
      labwareDefinitions,
      commands,
    }
  }
  // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
  return {} as ProtocolFile<{}>
}