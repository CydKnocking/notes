This script shows how to install and config zsh, oh-my-zsh and PowerLevel10k on Ubuntu.

"Oh My Zsh" is a framework for configuring "zsh". "PowerLevel10k" is a popular theme for "Oh My Zsh".

## zsh

First download zsh by
```
sudo apt update
sudo apt install zsh
```

Then set zsh to your default shell:
```
chsh -s $(which zsh)
```

And restart your computer.

## [Oh My Zsh](https://ohmyz.sh/)

```
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

## [PowerLevel10k](https://github.com/romkatv/powerlevel10k)

### Prepare font

[Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) is needed for full choice of style options.

Specifically, the font family `MesloLGS NF` is needed. Please download `Meslo.tar.xz` from the latest [releases](https://github.com/ryanoasis/nerd-fonts/releases), unzip and install `MesloLGSNerdFont-{Regular, Italic, Bold, BoldItalic}.ttf`.

### Download and config

Download by
```
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
```

Then run `vim .zshrc` under `/home/username/` and change theme by `ZSH_THEME="powerlevel10k/powerlevel10k"`.

Source the file by
```
source ~/.zshrc
```

Then the theme configurator for powerlevel10k should be automatically started.

You can also run the configurator manually by running
```
p10k configure
```
or you can use this to re-configure powerlevel10k theme.