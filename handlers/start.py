from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import get_main_menu_keyboard


async def start_command(message: types.Message, state: FSMContext):
    # Reset any active state
    await state.clear()
    
    first_name = message.from_user.first_name
    
    welcome_text = (
        f"👋 Welcome, {first_name}!\n\n"
        f"I'm your Crypto Assistant Bot. I can help you track cryptocurrency prices, "
        f"view market statistics, and monitor your favorite coins.\n\n"
        f"Use the buttons below to navigate:"
    )
    
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard()
    )


def register_start_handlers(dp):
    """
    Register all start related handlers
    """
    router = Router()
    router.message.register(start_command, Command(commands=["start"]))
    dp.include_router(router)