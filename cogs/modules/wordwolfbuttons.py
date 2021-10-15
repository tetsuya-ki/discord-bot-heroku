from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle

CUSTOM_ID_JOIN_WORD_WOLF  = 'ww_join_buttons'
CUSTOM_ID_LEAVE_WORD_WOLF = 'ww_leave_buttons'
CUSTOM_ID_START_WORD_WOLF = 'ww_start_buttons'
CUSTOM_ID_EXTEND_WORD_WOLF = 'ww_extend_buttons'

join_buttons = [
    create_button(
        style=ButtonStyle.green,
        label="参加する",
        custom_id=CUSTOM_ID_JOIN_WORD_WOLF
    ),
]
join_action_row = create_actionrow(*join_buttons)
leave_buttons = [
    create_button(
        style=ButtonStyle.red,
        label="離脱する",
        custom_id=CUSTOM_ID_LEAVE_WORD_WOLF
    ),
]
leave_action_row = create_actionrow(*leave_buttons)
start_buttons = [
    create_button(
        style=ButtonStyle.blue,
        label="開始する",
        custom_id=CUSTOM_ID_START_WORD_WOLF
    ),
]
start_action_row = create_actionrow(*start_buttons)
ww_extend_buttons = [
        create_button(
            style=ButtonStyle.gray,
            label='延長する',
            custom_id=CUSTOM_ID_EXTEND_WORD_WOLF
        ),
    ]
ww_extend_action_row = create_actionrow(*ww_extend_buttons)