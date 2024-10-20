
`chmod` is used to change permissions of files. If you wanna change the owner of files, please refer to chown.

usage: `chmod [-param][<permission_range>+/-/=<permission_setting>] file/directory`

- Change permission for "some user": `chmod [u/g/o/a][+/-/=][r/w/x/-] file`
  - `[u/g/o/a]` stands for "some user"
    - `u` User, the owner of file
    - `g` Group, the group owner of file
    - `o` Other, other users and groups except `u` and `g`
    - `a` All.
  - `[+/-/=]`: add permission / cancel permission / cancel all previous permissions and add the only permission
  - `[r/w/x/-]`: read / write / execute / none permission

- Change permission simultaneously for user(`x`), group(`y`) and others(`z`): `chmod [xyz] file`
  - `x y z` are integers, the sum of read(4), write(2) and execute(1).
  - eg: `chmod 764 file1`. User = 7 (4+2+1) r+w+x, group = 6 (4+2) r+w, other = 4 r.

- Params:
  - `-c` report when changes are made
  - `-f` do not output errors
  - `-R` change permissions for directory and sub files recursively.
  - `-v` output detailed logs
