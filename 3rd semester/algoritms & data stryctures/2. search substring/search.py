from typing import Optional
from enum import StrEnum

class Method(StrEnum):
    FIRST = "first",
    LAST = "last"



def search(
        string: str, 
        sub_string: str | list[str],
        case_sensitivity: bool = False,
        method: str=Method.FIRST, 
        count: Optional[int]=None,
    ) -> Optional[tuple[int, ...] | dict[str, tuple[int, ...]]]:

        if isinstance(sub_string, str):
            sub_string = [sub_string]
        
        source_string = string

        # case sensitivity logic
        string = string.upper() if not case_sensitivity else string

        # different search method logic
        # string = string if method == Method.FIRST else string[::-1]
        # sub_string = [sb_string[::-1] for sb_string in sub_string]

        result = {}

        for sb_string in sub_string:
            # case sensitivity logic
            case_sb_strint = sb_string.upper() if not case_sensitivity else sb_string
            result[sb_string] = single_search(
                string, 
                case_sb_strint,
                method,
                count
            )

            
        # If we have only one sub string we must returnt just turple
        if len(result) == 1:
            result = list(result.values())[0]
            return result if result else None
        # Else we must return dict with turples
        return result



def single_search(
        string: str,
        sub_string: str, 
        method: str='first', 
        count: Optional[int]=None,
    ) -> Optional[tuple[int, ...]]:
        """sub function to calculate single string."""
        prefixes = [0]*len(sub_string)
        j = 0
        i = 1

        if method == Method.LAST:
            string = string[::-1]
            sub_string = sub_string[::-1]

        # calculate suffix and preffix
        while i < len(sub_string):
            if sub_string[j] == sub_string[i]:
                prefixes[i] = j+1
                i += 1
                j += 1
            else:
                if j == 0:
                    prefixes[i] = 0
                    i += 1
                else:
                    j = prefixes[j-1]



        m = len(sub_string)
        n = len(string)

        i = 0
        j = 0
        cur_count = 0
        result = []

        # search single substring logic
        while i < n:
            if string[i] == sub_string[j]:
                i += 1
                j += 1
                if j == m:
                    cur_count +=1
                    result.append(i-m)
                    if count and cur_count == count:
                        break
                    j=0
            else:
                if j > 0:
                    j = prefixes[j-1]
                else:
                    i += 1

        if method == Method.LAST:
            result = result[::-1]

        return tuple(result)

sub_string = "лилила"
string = "лилилось лилилась Лилила лилила"

# print(search(string, sub_string, count=2, case_sensitivity=False))

# ('aaa', 'a', False, 'last', 2, (2, 1)),

print(search(
    string="aaa",
    sub_string="a",
    case_sensitivity=False,
    method="last",
    count=2,
))