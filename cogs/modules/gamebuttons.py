from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle

CUSTOM_ID_JOIN_WORD_WOLF  = 'ww_join_buttons'
CUSTOM_ID_LEAVE_WORD_WOLF = 'ww_leave_buttons'
CUSTOM_ID_START_WORD_WOLF = 'ww_start_buttons'
CUSTOM_ID_EXTEND_WORD_WOLF = 'ww_extend_buttons'
CUSTOM_ID_JOIN_NGGAME  = 'ng_join_buttons'
CUSTOM_ID_LEAVE_NGGAME = 'ng_leave_buttons'
CUSTOM_ID_START_NGGAME = 'ng_start_buttons'
CUSTOM_ID_EXTEND_NGGAME = 'ng_extend_buttons'
CUSTOM_ID_JOIN_COYOTE  = 'cy_join_buttons'
CUSTOM_ID_LEAVE_COYOTE = 'cy_leave_buttons'
CUSTOM_ID_START_COYOTE = 'cy_start_buttons'
CUSTOM_ID_EXTEND_COYOTE = 'cy_extend_buttons'
CUSTOM_ID_START_COYOTE_SET_DECK = 'cyw_start_buttons'
CUSTOM_ID_JOIN_OHGIRI  = 'oh_join_buttons'
CUSTOM_ID_LEAVE_OHGIRI = 'oh_leave_buttons'
CUSTOM_ID_START_OHGIRI = 'oh_start_buttons'
CUSTOM_ID_EXTEND_OHGIRI = 'oh_extend_buttons'

ww_join_buttons = [
    create_button(
        style=ButtonStyle.green,
        label="参加する",
        custom_id=CUSTOM_ID_JOIN_WORD_WOLF
    ),
]
ww_join_action_row = create_actionrow(*ww_join_buttons)
ww_leave_buttons = [
    create_button(
        style=ButtonStyle.red,
        label="離脱する",
        custom_id=CUSTOM_ID_LEAVE_WORD_WOLF
    ),
]
ww_leave_action_row = create_actionrow(*ww_leave_buttons)
ww_start_buttons = [
    create_button(
        style=ButtonStyle.blue,
        label="開始する",
        custom_id=CUSTOM_ID_START_WORD_WOLF
    ),
]
ww_start_action_row = create_actionrow(*ww_start_buttons)
ww_extend_buttons = [
        create_button(
            style=ButtonStyle.gray,
            label='延長する',
            custom_id=CUSTOM_ID_EXTEND_WORD_WOLF
        ),
    ]
ww_extend_action_row = create_actionrow(*ww_extend_buttons)

ng_join_buttons = [
    create_button(
        style=ButtonStyle.green,
        label="参加する",
        custom_id=CUSTOM_ID_JOIN_NGGAME
    ),
]
ng_join_action_row = create_actionrow(*ng_join_buttons)
ng_leave_buttons = [
    create_button(
        style=ButtonStyle.red,
        label="離脱する",
        custom_id=CUSTOM_ID_LEAVE_NGGAME
    ),
]
ng_leave_action_row = create_actionrow(*ng_leave_buttons)
ng_start_buttons = [
    create_button(
        style=ButtonStyle.blue,
        label="開始する",
        custom_id=CUSTOM_ID_START_NGGAME
    ),
]
ng_start_action_row = create_actionrow(*ng_start_buttons)
ng_extend_buttons = [
        create_button(
            style=ButtonStyle.gray,
            label='延長する',
            custom_id=CUSTOM_ID_EXTEND_NGGAME
        ),
    ]
ng_extend_action_row = create_actionrow(*ng_extend_buttons)

cy_join_buttons = [
    create_button(
        style=ButtonStyle.green,
        label="参加する",
        custom_id=CUSTOM_ID_JOIN_COYOTE
    ),
]
cy_join_action_row = create_actionrow(*cy_join_buttons)
cy_leave_buttons = [
    create_button(
        style=ButtonStyle.red,
        label="離脱する",
        custom_id=CUSTOM_ID_LEAVE_COYOTE
    ),
]
cy_leave_action_row = create_actionrow(*cy_leave_buttons)
cy_start_buttons = [
    create_button(
        style=ButtonStyle.blue,
        label="開始する",
        custom_id=CUSTOM_ID_START_COYOTE
    ),
]
cy_start_action_row = create_actionrow(*cy_start_buttons)
cy_extend_buttons = [
        create_button(
            style=ButtonStyle.gray,
            label='延長する',
            custom_id=CUSTOM_ID_EXTEND_COYOTE
        ),
    ]
cy_extend_action_row = create_actionrow(*cy_extend_buttons)
cyw_start_action_row = [
        create_button(
            style=ButtonStyle.gray,
            label='延長する',
            custom_id=CUSTOM_ID_START_COYOTE_SET_DECK
        ),
    ]
cyw_start_action_row = create_actionrow(*cyw_start_action_row)

oh_join_buttons = [
    create_button(
        style=ButtonStyle.green,
        label="参加する",
        custom_id=CUSTOM_ID_JOIN_OHGIRI
    ),
]
oh_join_action_row = create_actionrow(*oh_join_buttons)
oh_leave_buttons = [
    create_button(
        style=ButtonStyle.red,
        label="離脱する",
        custom_id=CUSTOM_ID_LEAVE_OHGIRI
    ),
]
oh_leave_action_row = create_actionrow(*oh_leave_buttons)
oh_start_buttons = [
    create_button(
        style=ButtonStyle.blue,
        label="開始する",
        custom_id=CUSTOM_ID_START_OHGIRI
    ),
]
oh_start_action_row = create_actionrow(*oh_start_buttons)
oh_extend_buttons = [
        create_button(
            style=ButtonStyle.gray,
            label='延長する',
            custom_id=CUSTOM_ID_EXTEND_OHGIRI
        ),
    ]
oh_extend_action_row = create_actionrow(*oh_extend_buttons)