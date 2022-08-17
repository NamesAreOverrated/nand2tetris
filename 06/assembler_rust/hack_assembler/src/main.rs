use std::{env, fs};

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        panic!("Not enough arguments!");
    }

    let asm_file = fs::read_to_string(&args[1]);

    match translate(&asm_file.unwrap()) {
        Ok(i) => {
            fs::write(&args[2], i).unwrap();
        }

        Err(i) => {
            panic!("{}", i)
        }
    }
}

fn translate(file: &str) -> Result<String, &str> {
    let mut dic = std::collections::HashMap::new();

    let mut register_index = 0;
    let register_max = 16384;

    for n in 0..16 {
        dic.entry(format!("R{}", n)).or_insert(n);
        register_index += 1;
    }
    dic.entry(String::from("SCREEN")).or_insert(16384);
    dic.entry(String::from("KBD")).or_insert(24576);

    let mut line_count = 0;

    for line in file.split('\n') {
        let line = line.trim();
        if line.starts_with("//") || line.is_empty() {
            continue;
        }
        if line.starts_with("(") {
            let mut label = String::new();
            for c in line.chars() {
                if c == '(' {
                    continue;
                }
                if c == ')' {
                    break;
                }
                if c == ' ' {
                    continue;
                }
                label.push(c);
            }

            if !dic.contains_key(&label) {
                dic.entry(label).or_insert(line_count);
            }

            continue;
        }

        line_count += 1;
    }
    let mut translated_lines = String::new();
    for line in file.split('\n') {
        let line = line.trim();
        if line.starts_with("//") || line.is_empty() || line.starts_with("(") {
            continue;
        }

        if line.starts_with('@') {
            let mut var_name = String::new();
            for c in line[1..].chars() {
                if c == '/' {
                    break;
                }
                if c == ' ' {
                    continue;
                }
                var_name.push(c);
            }

            let mut is_num = true;
            for c in var_name.chars() {
                if !c.is_numeric() {
                    is_num = false;
                }
            }
            if is_num && var_name.parse::<i32>().unwrap() <= register_max {
                translated_lines += "0";
                translated_lines += &format!("{:0>15b}", var_name.parse::<i32>().unwrap());
            } else {
                if !dic.contains_key(&var_name) {
                    dic.entry(var_name.clone()).or_insert(register_index);
                    register_index += 1;
                    if register_index >= register_max {
                        panic!("Reached max variable count!")
                    }
                }

                translated_lines += "0";
                translated_lines += &format!("{:0>15b}", dic[&var_name]);
            }
        } else {
            let mut is_dest_stopped = !line.contains("=");
            let mut dest = String::new();
            let mut is_comp_stopped = false;
            let mut comp = String::new();
            let mut jump = String::new();

            for c in line.chars() {
                if c == '/' {
                    break;
                }
                if c == ' ' {
                    continue;
                }
                if c == '=' {
                    is_dest_stopped = true;
                    continue;
                }
                if is_dest_stopped {
                    if c == ';' {
                        is_comp_stopped = true;
                        continue;
                    }
                    if is_comp_stopped {
                        jump.push(c);
                    } else {
                        comp.push(c);
                    }
                } else {
                    dest.push(c);
                }
            }
            translated_lines += "111";

            match comp.as_str() {
                "1" => translated_lines += "0111111",

                "-1" => translated_lines += "0111010",

                "D" => translated_lines += "0001100",

                "A" => translated_lines += "0110000",
                "M" => translated_lines += "1110000",

                "!D" => translated_lines += "0001101",

                "!A" => translated_lines += "0110001",
                "!M" => translated_lines += "1110001",

                "-D" => translated_lines += "0001111",

                "-A" => translated_lines += "0110001",
                "-M" => translated_lines += "1110001",

                "D+1" => translated_lines += "0011111",

                "A+1" => translated_lines += "0110111",
                "M+1" => translated_lines += "1110111",

                "D-1" => translated_lines += "0001110",

                "A-1" => translated_lines += "0110010",
                "M-1" => translated_lines += "1110010",

                "D+A" => translated_lines += "0000010",
                "D+M" => translated_lines += "1000010",

                "D-A" => translated_lines += "0010011",
                "D-M" => translated_lines += "1010011",

                "A-D" => translated_lines += "0000111",
                "M-D" => translated_lines += "1000111",

                "D&A" => translated_lines += "0000000",
                "D&M" => translated_lines += "1000000",

                "D|A" => translated_lines += "0010101",
                "D|M" => translated_lines += "1010101",
                _other => translated_lines += "0101010",
            }

            if dest.is_empty() || dest.as_str() == "null" {
                translated_lines += "000";
            } else {
                if dest.contains("A") {
                    translated_lines += "1";
                } else {
                    translated_lines += "0";
                }
                if dest.contains("D") {
                    translated_lines += "1";
                } else {
                    translated_lines += "0";
                }
                if dest.contains("M") {
                    translated_lines += "1";
                } else {
                    translated_lines += "0";
                }
            }

            match jump.as_str() {
                "JGT" => translated_lines += "001",
                "JEQ" => translated_lines += "010",
                "JGE" => translated_lines += "011",
                "JLT" => translated_lines += "100",
                "JNE" => translated_lines += "101",
                "JLE" => translated_lines += "110",
                "JMP" => translated_lines += "111",

                _other => translated_lines += "000",
            }
        }
        translated_lines.push('\n');
    }
    Ok(translated_lines)
}
