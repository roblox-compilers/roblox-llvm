import chalk from "chalk";

function error(message) {
    console.log(chalk.red.bold('error ') + chalk.gray("RASM: ") + message);
}

function warn(message) {
    console.log(chalk.yellow.bold('warn ') + chalk.gray("RASM: ") + message);
}

function info(message) {
    console.log(chalk.blue.bold('info ') + chalk.gray("RASM: ") + message);
}

export default {
    error,
    warn,
    info
};