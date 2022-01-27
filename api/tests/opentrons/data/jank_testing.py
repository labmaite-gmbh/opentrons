metadata = {
    "apiLevel": "2.12",
}

REPEAT_COUNT = 100


def run(context):
    tip_rack = context.load_labware("opentrons_96_tiprack_300ul", 1)
    labware = context.load_labware("corning_96_wellplate_360ul_flat", 2)
    pipette = context.load_instrument("p300_single_gen2", "right", [tip_rack])

    pipette.pick_up_tip()
    pipette.move_to(labware.wells()[0].top())

    for i in range(REPEAT_COUNT):
        pipette.touch_tip()

    pipette.return_tip()
