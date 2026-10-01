#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "orders.h"

int main(void) {
    repository repo = {.skus = {"mug"}, .stock = {1}, .count = 1};
    int id = 0;
    const char *failed = NULL;

    assert(status_for(orders_place(&repo, NULL, 0, &id, &failed)) == 400);

    item too_many[] = {{"mug", 5}};
    assert(status_for(orders_place(&repo, too_many, 1, &id, &failed)) == 409);
    assert(strcmp(failed, "mug") == 0);

    item one[] = {{"mug", 1}};
    assert(status_for(orders_place(&repo, one, 1, &id, &failed)) == 201);
    assert(id == 1 && repo.stock[0] == 0);
    puts("ok: return codes mapped to 400, 409 and 201");
    return 0;
}
