from math import ceil
from typing import TYPE_CHECKING

from khl import User
from khl_card import CardMessage, CardMessageBuilder, CardBuilder, ContainerBuilder, Image, ActionGroupBuilder, \
    Button, Kmarkdown, ThemeTypes, Paragraph, SizeTypes, ActionGroup, Context

from ...database.models.user_info import UserInfo, VipTypes
from ...utils.config import config

if TYPE_CHECKING:
    from ...tofu_bot import TofuBot


async def checkExists(kook_id: str) -> bool:
    if await UserInfo.get_or_none(kook_id=kook_id):
        return True
    else:
        return False


async def main_panel(bot: 'TofuBot', need_online_count: bool = False, check_exists: bool = True, kook_id: str = '') -> CardMessage:
    cb = CardBuilder()
    # if need_online_count:
    #     cb.section(Kmarkdown.bold(f'服务器实时在线人数为: {len(bot.rcon.player_list())}'))
    
    cb.container(
        ContainerBuilder()
        .add(Image('https://img.kookapp.cn/assets/2022-07/ysj2qWpzEP0sg0go.gif'))
        .build()
    )

    if check_exists:
        user_exists = await checkExists(kook_id)
        if not user_exists:
            cb.section(Kmarkdown.bold('您尚未注册，点击 `注册` 按钮，按照提示消息进行操作即可'))
            cb.divider()
            cb.action_group(
                ActionGroupBuilder()
                .add(Button(Kmarkdown('注册'), ThemeTypes.PRIMARY, click='return-val', value='register'))
                .build()
            )
            cb.context(Context(Kmarkdown('注册成功后，可进行 `存龙`、`取龙`、`孵化龙蛋`、`龙蛋换龙` 等操作'))).build()
            cb.context(Context(Kmarkdown('可以在机器人私聊使用 `/面板` 命令来呼出面板'))).build()
        else:
            cb.section(Kmarkdown.bold('亲爱的注册用户，您好！'))
            cb.divider()
            cb.action_group(
                ActionGroupBuilder()
                .add(Button(Kmarkdown('我的库存'), ThemeTypes.INFO, click='return-val', value='query'))
                .add(Button(Kmarkdown('存龙'), ThemeTypes.INFO, click='return-val', value='save_dragon'))
                .add(Button(Kmarkdown('取龙'), ThemeTypes.INFO, click='return-val', value='get_dragon'))
                .build()
            )
            cb.action_group(
                ActionGroupBuilder()
                .add(Button(Kmarkdown('孵化龙蛋'), ThemeTypes.WARNING, click='return-val', value='hatch'))
                .add(Button(Kmarkdown('龙蛋换龙'), ThemeTypes.WARNING, click='return-val', value='dragon_egg'))
                # .add(Button(Kmarkdown('外挂举报'), ThemeTypes.WARNING, click='return-val', value='_'))
                .build()
            )
            # cb.divider()
            # cb.action_group(
            #     ActionGroupBuilder()
            #     .add(Button(Kmarkdown('购买龙蛋'), ThemeTypes.DANGER, click='return-val', value='_'))
            #     .add(Button(Kmarkdown('开通会员'), ThemeTypes.DANGER, click='return-val', value='_'))
            #     .add(Button(Kmarkdown('赞助本服'), ThemeTypes.DANGER, click='return-val', value='_'))
            #     .build()
            # )
            cb.divider()
            cb.context(Context(Kmarkdown('可以频道内使用 `/面板` 命令呼出此窗口'))).build()
        return CardMessageBuilder().card(cb.build()).build()
    # else:
    #     (
    #         cb
    #         .container(
    #             ContainerBuilder()
    #             .add(Image('https://img.kookapp.cn/assets/2022-07/ysj2qWpzEP0sg0go.gif'))
    #             .build()
    #         )
    #         .divider()
    #         .action_group(
    #             ActionGroupBuilder()
    #             .add(Button(Kmarkdown('注册'), ThemeTypes.INFO, click='return-val', value='register'))
    #             .add(Button(Kmarkdown('取龙'), ThemeTypes.INFO, click='return-val', value='get_dragon'))
    #             .add(Button(Kmarkdown('存龙'), ThemeTypes.INFO, click='return-val', value='save_dragon'))
    #             #.add(Button(Kmarkdown('查询'), ThemeTypes.INFO, click='return-val', value='query'))
    #             .build()
    #         )
    #         .divider()
    #         .action_group(
    #             ActionGroupBuilder()
    #             .add(Button(Kmarkdown('查询'), ThemeTypes.INFO, click='return-val', value='query'))
    #             .add(Button(Kmarkdown('孵化'), ThemeTypes.INFO, click='return-val', value='hatch'))
    #             #.add(Button(Kmarkdown('开蛋'), ThemeTypes.INFO, click='return-val', value='open_egg'))
    #             .add(Button(Kmarkdown('龙蛋换龙'), ThemeTypes.INFO, click='return-val', value='dragon_egg'))
    #             # .add(Button(Kmarkdown('外挂举报'), ThemeTypes.SUCCESS, click='return-val', value='_'))
    #             .build()
    #         )
    #         .context(Context(Kmarkdown('可以在机器人私聊使用 `/面板` 命令来呼出面板')))
    #         .build()
    #     )
    #     return CardMessageBuilder().card(cb.build()).build()


async def info_panel(user: User, need_back_button: bool = True):
    user_info = await UserInfo.get_or_none(kook_id=user.id)
    # if user_info is None:
    #     cb = CardBuilder().header("请注册后再来使用~")
    #     if need_back_button:
    #         cb.action_group(
    #             ActionGroupBuilder()
    #             .add(Button(Kmarkdown('返回'), ThemeTypes.DANGER, click='return-val', value='back_main'))
    #             .build()
    #         )
    #     return CardMessage(cb.build())
    # header_text = (f'尊敬的 `{user_info.vip_type.to_chinese()}` 会员，'
    #                if user_info.vip_type != VipTypes.NONE else '') + '以下为您的库存信息：'

    inv_col1 = ''
    inv_col2 = ''
    inv_col3 = ''

    for i, name in enumerate(config.dragon_info.keys(), start=1):
        if name not in user_info.dragon_inventory:
            continue
        if i % 3 == 1:
            inv_col1 += f'{config.dragon_info[name].translate_name}: {user_info.dragon_inventory[name]}\n'
        elif i % 3 == 2:
            inv_col2 += f'{config.dragon_info[name].translate_name}: {user_info.dragon_inventory[name]}\n'
        elif i % 3 == 0:
            inv_col3 += f'{config.dragon_info[name].translate_name}: {user_info.dragon_inventory[name]}\n'

    inv_col1.rstrip('\n')
    inv_col2.rstrip('\n')
    inv_col3.rstrip('\n')

    vip_text = '非会员用户'
    vip_days = ''
    vip_get_eggs = ''

    if user_info.vip_type != VipTypes.NONE and user_info.vip_days > 0:
        vip_text = f'亲爱的 `{user_info.vip_type.to_chinese()}会员`，您好！\n'
        vip_days = f'会员有效期剩余：`{user_info.vip_days}天`\n'
        vip_get_eggs = f'在会员有效期内，您每日将获赠 `{user_info.vip_type.get_egg_everyday()}` 个龙蛋\n'

    monthly_card_text = '您没有开通孵化月卡\n'
    if user_info.monthly_card_days > 0:
        monthly_card_text = f'孵化月卡生效中，剩余: `{user_info.monthly_card_days}天`\n'

    cb = (
        CardBuilder()
        .header('以下为您的库存信息：')
        .divider()
        .section(
            Kmarkdown.bold(f'用户名：{user.nickname}\n') +
            Kmarkdown(f'注册序列：{user_info.id}\n') +
            Kmarkdown(f'KOOK ID：{user_info.kook_id}\n') +
            Kmarkdown(f'Steam ID：{user_info.steam_17_id}\n'),
            accessory=Image(user.avatar, SizeTypes.SM)
        )
        .divider()
        .section(
            Kmarkdown(vip_text + vip_get_eggs + vip_days)
        )
        .divider()
        .section(
            Kmarkdown.bold(monthly_card_text) +
            Kmarkdown(f'当前拥有龙蛋：`{user_info.dragon_egg}个`\n') +
            Kmarkdown(f'当前孵化进度：`{user_info.dragon_egg_hatch_percent}%`\n') +
            Kmarkdown(f'上次孵化时间：{user_info.last_dragon_egg_hatch_date.strftime("%Y-%m-%d %H:%M:%S") if user_info.last_dragon_egg_hatch_date else "-"}\n\n') + 
            Kmarkdown.bold('孵化规则：\n') +
            Kmarkdown('1.普通用户每天可孵化 1次，孵化月卡用户每天可孵化 2次\n') +
            Kmarkdown('2.每次孵化最大 20%，当孵化进度为 100% 时，即可获得 1枚 龙蛋\n')
        )
        # .divider()
        # .section(Paragraph(2, [
        #     Kmarkdown(
        #         f'您现在拥有龙蛋 {user_info.dragon_egg} 个\n{"月卡生效中" if user_info.monthly_card_days > 0 else "未拥有月卡"}, 月卡用户每日可孵化两次\n当前孵化进度为 {user_info.dragon_egg_hatch_percent}%'),
        #     Kmarkdown(f'每日赠送{user_info.vip_type.get_egg_everyday()}个龙蛋 剩余 {user_info.vip_days} 天\n'
        #               if user_info.vip_type != VipTypes.NONE else '\n') +
        #     Kmarkdown(f'月卡剩余{user_info.monthly_card_days}天\n' if user_info.monthly_card_days > 0 else '\n') +
        #     Kmarkdown(
        #         f'上次孵化时间：\n{user_info.last_dragon_egg_hatch_date.strftime("%Y-%m-%d %H:%M:%S") if user_info.last_dragon_egg_hatch_date else "无"}')
        # ]))
        .divider()
        .section(Kmarkdown.bold("您的仓库有："))
        .section(Paragraph(3, [
            Kmarkdown(inv_col1),
            Kmarkdown(inv_col2),
            Kmarkdown(inv_col3)
        ]))
    )

    if need_back_button:
        cb.action_group(
            ActionGroupBuilder()
            .add(Button(Kmarkdown('返回'), ThemeTypes.DANGER, click='return-val', value='back_main'))
            .build()
        )

    return CardMessageBuilder().card(
        cb.build()
    ).build()


async def dragon_egg_panel(user: User):
    user_info = await UserInfo.get_or_none(kook_id=user.id)
    # if user_info is None:
    #     return CardMessage(CardBuilder().header("请注册后再来使用~").build())

    button_list = []
    for name in config.dragon_info:
        info = config.dragon_info[name]
        if info.cost == -1:
            continue
        button_list.append(Button(
            Kmarkdown(f'\t{info.cost}蛋 = {info.count}{info.translate_name}\t'),
            theme=ThemeTypes.SUCCESS,
            click='return-val',
            value=f'buy_{name}'
        ))

    action_group_list = list(map(lambda x: button_list[x * 2:x * 2 + 2], list(range(0, ceil(len(button_list) / 2)))))

    cb = CardBuilder().section(Kmarkdown(f'点击下方按钮选择你想兑换的龙。您当前有 **{user_info.dragon_egg}** 龙蛋。'))

    for action_group in action_group_list:
        cb.action_group(ActionGroup(*action_group))

    cb.action_group(
        ActionGroupBuilder()
        .add(Button(Kmarkdown('返回'), ThemeTypes.DANGER, click='return-val', value='back_main'))
        .build()
    )
    return CardMessageBuilder().card(
        cb.build()
    ).build()
